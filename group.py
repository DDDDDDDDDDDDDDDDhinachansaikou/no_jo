
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

    if not group_name.strip():
        st.warning("群組名稱不能為空")
        return

    # 全域檢查是否有相同名稱
    all_group_names = set()
    for entry in df["groups"].fillna(""):
        all_group_names.update(g.strip() for g in entry.split(",") if g.strip())
    if group_name in all_group_names:
        st.error("群組名稱已存在，請換一個")
        return

    # 將此群組加入建立者資料
    idx = df[df["user_id"] == user_id].index[0]
    current_groups = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()
    current_groups.add(group_name)
    df.at[idx, 'groups'] = ','.join(sorted(current_groups))

    # 加入群組成員欄位（確保只加一次）
    current_members = df.at[idx, 'group_members']
    entry = f"|{group_name}:{user_id}"
    if entry not in current_members:
        df.at[idx, 'group_members'] += entry

    save_df(df)
    st.success(f"群組「{group_name}」建立成功，並已自動加入群組")


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
def show_group_availability(group_map):
    import streamlit as st
    from datetime import datetime
    from calendar_tools import display_calendar_view

    st.subheader("群組成員空閒時間")

    if not group_map:
        st.info("你目前沒有加入任何群組")
        return

    group_names = list(group_map.keys())
    selected_group = st.selectbox("選擇群組", group_names, key="group_selector")

    # 安全取得群組成員
    members = group_map.get(selected_group, [])
    if not members:
        st.info("這個群組尚無其他成員")
        return

    selected_user = st.selectbox("選擇要查看的成員", members, key=f"user_selector_{selected_group}")

    # 若切換群組或成員，自動重設月曆
    if st.session_state.get("last_calendar_group") != selected_group or st.session_state.get("last_calendar_user") != selected_user:
        for suffix in ["show_year", "show_month", "last_click"]:
            st.session_state.pop(f"{selected_user}_{suffix}", None)
        st.session_state["last_calendar_group"] = selected_group
        st.session_state["last_calendar_user"] = selected_user

    display_calendar_view(selected_user)
def render_group_management_ui(user_id):
    st.subheader("所屬群組與成員")

    groups = list_groups_and_members(user_id)
    if not groups:
        st.info("您尚未加入任何群組")
    else:
        for gname, members in groups.items():
            st.markdown(f"#### {gname}")
            st.markdown(f"成員：{', '.join(members)}")

            if st.button("刪除群組", key=f"delete_{gname}"):
                delete_group(user_id, gname)
                st.rerun()

            for member in members:
                if member != user_id:
                    if st.button(f"移除 {member}", key=f"kick_{gname}_{member}"):
                        remove_member_from_group(user_id, gname, member)
                        st.rerun()

        st.markdown("---")
    st.subheader("移除群組成員")

    if groups:
        selected_group_for_kick = st.selectbox("選擇群組", list(groups.keys()), key="kick_group_select")
        kickable_members = [m for m in groups[selected_group_for_kick] if m != user_id]

        if kickable_members:
            selected_member_to_kick = st.selectbox("選擇要移除的成員", kickable_members, key="kick_member_select")
            if st.button("移除該成員"):
                remove_member_from_group(user_id, selected_group_for_kick, selected_member_to_kick)
                st.success(f"{selected_member_to_kick} 已被從 {selected_group_for_kick} 移除")
                st.rerun()
        else:
            st.info("該群組沒有其他成員可移除")

    
        st.markdown("---")
    st.subheader("刪除群組")

    if groups:
        selected_group_for_delete = st.selectbox("選擇要刪除的群組", list(groups.keys()), key="delete_group_selector")
        if st.button("刪除選定群組"):
            delete_group(user_id, selected_group_for_delete)
            st.success(f"群組 {selected_group_for_delete} 已刪除")
            st.rerun()
    else:
        st.info("您尚未加入任何群組")

    st.subheader("邀請好友加入群組")
    friend_to_invite = st.text_input("好友 ID", key="friend_invite_input")
    group_target = st.selectbox("選擇要加入的群組", list(groups.keys()) if groups else [], key="group_invite_target")
    if st.button("邀請好友"):
        invite_friend_to_group(user_id, friend_to_invite, group_target)
        st.rerun()

def remove_member_from_group(user_id, group_name, target_id):
    df = get_df()
    df = ensure_group_columns(df)

    if target_id not in df['user_id'].values:
        st.error("成員不存在")
        return

    idx = df[df['user_id'] == target_id].index[0]
    group_list = set(df.at[idx, 'groups'].split(',')) if df.at[idx, 'groups'] else set()

    if group_name in group_list:
        group_list.remove(group_name)
        df.at[idx, 'groups'] = ','.join(sorted(group_list))

    member_entry = f"|{group_name}:{target_id}"
    df.at[idx, 'group_members'] = df.at[idx, 'group_members'].replace(member_entry, '')

    save_df(df)

def delete_group(user_id, group_name):
    df = get_df()
    df = ensure_group_columns(df)
    for idx, row in df.iterrows():
        groups = set(row['groups'].split(',')) if row['groups'] else set()
        if group_name in groups:
            groups.remove(group_name)
            df.at[idx, 'groups'] = ','.join(sorted(groups))

        members = row['group_members']
        df.at[idx, 'group_members'] = '|'.join(
            [entry for entry in members.split('|') if not entry.startswith(f"{group_name}:")]
        )

    save_df(df)
    st.success(f"群組 {group_name} 已刪除")
