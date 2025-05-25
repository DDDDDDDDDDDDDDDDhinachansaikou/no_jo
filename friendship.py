
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
    df.loc[df['user_id'] == target_user, 'friend_requests'] = ','.join(target_requests_set)
    save_df(df)
    return "好友申請已送出"
