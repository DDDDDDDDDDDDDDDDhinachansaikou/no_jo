
import streamlit as st
from auth import authenticate_user, register_user
from availability import update_availability, find_users_by_date
from friendship import send_friend_request, accept_friend_request, reject_friend_request, list_friend_requests, list_friends, show_friend_list_with_availability
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
if st.session_state.authenticated:
    page_options = ["登記可用時間", "查詢可配對使用者", "送出好友申請", "回應好友申請", "查看好友清單", "登出"]
    if st.session_state.user_id == "GM":
        page_options.insert(-1, "管理介面")
else:
    page_options = ["登入", "註冊"]
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

elif selected_page == "登記可用時間":
    date_range = pd.date_range(date.today(), periods=30).tolist()
    selected = st.multiselect("選擇可用日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    if st.button("更新"):
        update_availability(st.session_state.user_id, [d.strftime("%Y-%m-%d") for d in selected])

elif selected_page == "查詢可配對使用者":
    date_range = pd.date_range(date.today(), periods=30).tolist()
    selected = st.multiselect("查詢日期", date_range, format_func=lambda d: d.strftime("%Y-%m-%d"))
    for d in selected:
        users = find_users_by_date(d.strftime("%Y-%m-%d"), st.session_state.user_id)
        st.write(f"{d.strftime('%Y-%m-%d')}: {', '.join(users) if users else '無'}")

elif selected_page == "送出好友申請":
    target = st.text_input("輸入對方 ID")
    if st.button("送出好友申請"):
        msg = send_friend_request(st.session_state.user_id, target)
        st.info(msg)

elif selected_page == "回應好友申請":
    requests = list_friend_requests(st.session_state.user_id)
    if not requests:
        st.info("目前沒有好友申請")
    for requester in requests:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"來自 {requester} 的好友申請")
        with col2:
            if st.button("接受", key=f"accept_{requester}"):
                msg = accept_friend_request(st.session_state.user_id, requester)
                st.success(msg)
                st.rerun()
            if st.button("拒絕", key=f"reject_{requester}"):
                msg = reject_friend_request(st.session_state.user_id, requester)
                st.info(msg)
                st.rerun()

elif selected_page == "查看好友清單":
    show_friend_list_with_availability(st.session_state.user_id)
    friends = list_friends(st.session_state.user_id)
    if not friends:
        st.info("您目前尚無好友")
    else:
        st.markdown("### 好友：")
        for f in friends:
            st.markdown(f"- {f}")


elif selected_page == "管理介面" and st.session_state.user_id == "GM":
    st.subheader("👑 GM 管理介面")
    df = get_df()
    st.dataframe(df)

elif selected_page == "登出":
    st.session_state.authenticated = False
    st.session_state.user_id = ""
    st.session_state.page = "登入"
    st.success("已登出")
    st.rerun()
