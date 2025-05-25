
import streamlit as st
from auth import authenticate_user, register_user
from availability import update_availability, find_users_by_date
from friendship import send_friend_request
from sheets import get_df
import pandas as pd
from datetime import date

st.title("多人會議可用時間系統")

# 初始化 session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'page' not in st.session_state:
    st.session_state.page = "登入"
if 'rerun_triggered' not in st.session_state:
    st.session_state.rerun_triggered = False

# 自動跳轉處理
if st.session_state.page == "登入成功" and not st.session_state.rerun_triggered:
    st.session_state.page = "登記可用時間"
    st.session_state.rerun_triggered = True
    st.rerun()

# 功能選單
page_options = ["登入", "註冊"]
if st.session_state.authenticated:
    page_options += ["登記可用時間", "查詢可配對使用者", "送出好友申請", "登出"]
selected_page = st.sidebar.radio("功能選單", page_options)
st.session_state.page = selected_page

# 頁面對應
if selected_page == "註冊":
    uid = st.text_input("新帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("註冊"):
        success, msg = register_user(uid, pw)
        st.success(msg) if success else st.error(msg)
elif selected_page == "登入":
    uid = st.text_input("帳號")
    pw = st.text_input("密碼", type="password")
    if st.button("登入"):
        if authenticate_user(uid, pw):
            st.session_state.authenticated = True
            st.session_state.user_id = uid
            st.success("登入成功")
            st.session_state.page = "登入成功"
            st.session_state.rerun_triggered = False
            st.rerun()
        else:
            st.error("帳號或密碼錯誤")
elif selected_page == "登記可用時間" and st.session_state.authenticated:
    date_range = pd.date_range(date.today(), periods=30).tolist()
    selected = st.multiselect("選擇可用日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    if st.button("更新"):
        update_availability(st.session_state.user_id, [d.strftime("%Y-%m-%d") for d in selected])
elif selected_page == "查詢可配對使用者" and st.session_state.authenticated:
    date_range = pd.date_range(date.today(), periods=30).tolist()
    selected = st.multiselect("查詢日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    for d in selected:
        users = find_users_by_date(d.strftime("%Y-%m-%d"), st.session_state.user_id)
        st.write(f"{d.strftime('%Y-%m-%d')}: {', '.join(users) if users else '無'}")
elif selected_page == "送出好友申請" and st.session_state.authenticated:
    target = st.text_input("輸入對方 ID")
    if st.button("送出好友申請"):
        msg = send_friend_request(st.session_state.user_id, target)
        st.info(msg)
elif selected_page == "登出":
    st.session_state.authenticated = False
    st.session_state.user_id = ""
    st.session_state.page = "登入"
    st.success("已登出")
    st.rerun()
