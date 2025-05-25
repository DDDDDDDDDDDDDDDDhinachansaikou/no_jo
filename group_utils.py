import pandas as pd
import os

GROUP_FILE = "group_table.csv"

def load_group_table():
    if os.path.exists(GROUP_FILE):
        return pd.read_csv(GROUP_FILE)
    else:
        return pd.DataFrame(columns=["group_name", "members"])

def save_group_table(df):
    df.to_csv(GROUP_FILE, index=False)

def create_group(user_id, group_name):
    df = load_group_table()
    if group_name in df["group_name"].values:
        return False, "群組已存在"
    new_row = {"group_name": group_name, "members": user_id}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_group_table(df)
    return True, "建立成功"

def invite_to_group(group_name, friend_id):
    df = load_group_table()
    if group_name not in df["group_name"].values:
        return False, "群組不存在"
    idx = df[df["group_name"] == group_name].index[0]
    current_members = set(df.at[idx, "members"].split(','))
    if friend_id in current_members:
        return False, "已在群組中"
    current_members.add(friend_id)
    df.at[idx, "members"] = ",".join(sorted(current_members))
    save_group_table(df)
    return True, "已加入群組"

def list_groups_for_user(user_id):
    df = load_group_table()
    user_groups = df[df["members"].str.contains(fr"\b{user_id}\b", na=False)]
    return {row["group_name"]: row["members"].split(',') for _, row in user_groups.iterrows()}

def remove_member(group_name, target_id):
    df = load_group_table()
    if group_name not in df["group_name"].values:
        return False
    idx = df[df["group_name"] == group_name].index[0]
    members = set(df.at[idx, "members"].split(','))
    if target_id in members:
        members.remove(target_id)
        if members:
            df.at[idx, "members"] = ",".join(sorted(members))
        else:
            df = df.drop(idx)
        save_group_table(df)
        return True
    return False

def delete_group(group_name):
    df = load_group_table()
    df = df[df["group_name"] != group_name]
    save_group_table(df)
