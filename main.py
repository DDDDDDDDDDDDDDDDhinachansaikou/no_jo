
import streamlit as st
from auth import authenticate_user, register_user
from availability import update_availability, find_users_by_date
from friendship import send_friend_request, accept_friend_request
from sheets import get_df
import pandas as pd
from datetime import date

st.title("多人會議可用時間系統")

# 初始化 session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""

page = st.sidebar.radio("選單", ["登入", "註冊", "登記可用時間", "查詢配對", "送出好友申請"])

if page == "註冊":
    uid = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("註冊"):
        success, msg = register_user(uid, pw)
        st.success(msg) if success else st.error(msg)

elif page == "登入":
    uid = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("登入"):
        if authenticate_user(uid, pw):
            st.session_state.authenticated = True
            st.session_state.user_id = uid
            st.success("登入成功")
        else:
            st.error("帳號或密碼錯誤")

elif page == "登記可用時間" and st.session_state.authenticated:
    st.subheader("選擇可用日期")
    date_range = pd.date_range(date.today(), periods=30).tolist()
    selected = st.multiselect("可用日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    if st.button("更新"):
        update_availability(st.session_state.user_id, [d.strftime("%Y-%m-%d") for d in selected])

elif page == "查詢配對" and st.session_state.authenticated:
    st.subheader("查詢可配對使用者")
    date_range = pd.date_range(date.today(), periods=30).tolist()
    selected = st.multiselect("查詢日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    for d in selected:
        users = find_users_by_date(d.strftime("%Y-%m-%d"), st.session_state.user_id)
        st.write(f"{d.strftime('%Y-%m-%d')}: {', '.join(users) if users else '無'}")

elif page == "送出好友申請" and st.session_state.authenticated:
    target = st.text_input("對象帳號")
    if st.button("送出"):
        msg = send_friend_request(st.session_state.user_id, target)
        st.info(msg)
