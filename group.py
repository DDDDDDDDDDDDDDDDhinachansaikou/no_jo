
import streamlit as st
import pandas as pd
from sheets import get_df, save_df
from calendar_tools import display_calendar_view

# 初始化群組欄位
def ensure_group_columns(df):
    if 'groups' not in df.columns:
        df['groups'] = ''
    if 'group_members' not in df.columns:
        df['group_members'] = ''
    return df

# 建立新群組
def create_group(user_id, group_name):
    df = get_df()
    df = ensure_group_columns(df)
    if not group_name:
        st.warning("群組名稱不能為空")
        return

    all_groups = df['groups'].tolist()
    if group_name in [g.strip() for group_list in all_groups for g in group_list.split(',')]:
        st.warning("群組名稱已存在")
        return

    idx = df[df['user_id'] == user_id].index[0]
    current_groups = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()
    current_groups.add(group_name)
    df.at[idx, 'groups'] = ','.join(sorted(current_groups))

    df.at[idx, 'group_members'] = df.at[idx, 'group_members'] + f'|{group_name}:{user_id}'
    save_df(df)
    st.success(f"群組 {group_name} 已建立")

# 邀請好友加入群組
def invite_friend_to_group(user_id, friend_id, group_name):
    df = get_df()
    df = ensure_group_columns(df)

    if friend_id not in df['user_id'].values:
        st.error("好友不存在")
        return

    friend_idx = df[df['user_id'] == friend_id].index[0]
    groups = set(df.at[friend_idx, 'groups'].split(',')) if df.at[friend_idx, 'groups'] else set()
    if group_name in groups:
        st.info(f"{friend_id} 已在群組中")
        return

    groups.add(group_name)
    df.at[friend_idx, 'groups'] = ','.join(sorted(groups))
    current_group_members = df.at[friend_idx, 'group_members']
    new_entry = f"|{group_name}:{friend_id}"
    if new_entry not in current_group_members:
        df.at[friend_idx, 'group_members'] += new_entry

    save_df(df)
    st.success(f"已邀請 {friend_id} 加入群組 {group_name}")

# 取得使用者群組與成員
def list_groups_and_members(user_id):
    df = get_df()
    df = ensure_group_columns(df)
    idx = df[df['user_id'] == user_id].index[0]
    user_groups = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()
    group_members_map = {}

    for group in user_groups:
        members = []
        for _, row in df.iterrows():
            if group in row.get('groups', ''):
                members.append(row['user_id'])
        group_members_map[group] = sorted(set(members))
    return group_members_map

# 顯示群組成員空閒日曆
def show_group_availability(group_name, members):
    st.subheader(f"群組 {group_name} 成員空閒時間")
    for member in members:
        st.markdown(f"**{member}**")
        display_calendar_view(member)
        st.markdown("---")
