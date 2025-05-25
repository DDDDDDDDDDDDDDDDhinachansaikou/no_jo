
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

def list_friends(user_id):
    df = get_df()
    idx = df[df['user_id'] == user_id].index[0]
    friends = df.at[idx, 'friends']
    return sorted(list(filter(None, friends.split(','))))
