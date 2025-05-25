
from sheets import get_df, save_df

def send_friend_request(current_user, target_user):
    if current_user == target_user:
        return "不能對自己發送好友申請"

    df = get_df()
    if target_user not in df['user_id'].values:
        return "使用者不存在"

    target_requests = df.loc[df['user_id'] == target_user, 'friend_requests'].values[0]
    target_requests_set = set(target_requests.split(',')) if target_requests else set()
    if current_user in target_requests_set:
        return "已發送好友申請，請等待回應"

    target_requests_set.add(current_user)
    df.loc[df['user_id'] == target_user, 'friend_requests'] = ','.join(sorted(target_requests_set))
    save_df(df)
    return "好友申請已送出"

def accept_friend_request(user_id, requester):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    friends = set(df.at[idx, 'friends'].split(',')) if df.at[idx, 'friends'] else set()
    friends.add(requester)
    df.at[idx, 'friends'] = ','.join(sorted(friends))

    req_idx = df[df['user_id'] == requester].index[0]
    req_friends = set(df.at[req_idx, 'friends'].split(',')) if df.at[req_idx, 'friends'] else set()
    req_friends.add(user_id)
    df.at[req_idx, 'friends'] = ','.join(sorted(req_friends))

    requests = set(df.at[idx, 'friend_requests'].split(',')) if df.at[idx, 'friend_requests'] else set()
    requests.discard(requester)
    df.at[idx, 'friend_requests'] = ','.join(sorted(requests))

    save_df(df)
    return "您已與對方成為好友"

def reject_friend_request(user_id, requester):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    requests = set(df.at[idx, 'friend_requests'].split(',')) if df.at[idx, 'friend_requests'] else set()
    requests.discard(requester)
    df.at[idx, 'friend_requests'] = ','.join(sorted(requests))
    save_df(df)
    return "已拒絕好友申請"

def list_friend_requests(user_id):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    requests = df.at[idx, 'friend_requests']
    return sorted(list(filter(None, requests.split(','))))

import streamlit as st

def show_friend_list_with_availability(current_user):
    friends = list_friends(current_user)
    if not friends:
        st.info("您目前尚無好友")
    else:
        st.markdown("### 好友清單（點擊展開空閒時間）")
        if "friend_view_states" not in st.session_state:
            st.session_state.friend_view_states = {}
        df = get_df()
        for friend in friends:
            if friend not in st.session_state.friend_view_states:
                st.session_state.friend_view_states[friend] = False

            with st.expander(f"{friend}", expanded=st.session_state.friend_view_states[friend]):
                friend_data = df[df['user_id'] == friend]
                if not friend_data.empty:
                    dates = friend_data.iloc[0]['available_dates']
                    date_list = [d.strip() for d in dates.split(',')] if dates else []
                    st.markdown(f"**空閒時間**：{'、'.join(date_list) if date_list else '尚未登記'}")
