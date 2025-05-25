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
    df.at[idx, 'friend_requests'] = ','.join(requests)

    save_df(df)
    return "您已與對方成為好友"
