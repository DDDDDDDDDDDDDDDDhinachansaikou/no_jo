import streamlit as st
import calendar
import time
from datetime import datetime
from sheets import get_df

# ✅ 用於「選擇」可用日期：顯示並點選選取
def display_calendar_view(user_id):
    today = datetime.today()

    # 🔁 每次切換對象 → 自動 reset 畫面
    if "last_display_user" not in st.session_state:
        st.session_state["last_display_user"] = user_id
    if st.session_state["last_display_user"] != user_id:
        st.session_state[f"{user_id}_show_year"] = today.year
        st.session_state[f"{user_id}_show_month"] = today.month
        st.session_state[f"{user_id}_last_click"] = 0.0
        st.session_state["last_display_user"] = user_id

    if f"{user_id}_show_year" not in st.session_state:
        st.session_state[f"{user_id}_show_year"] = today.year
    if f"{user_id}_show_month" not in st.session_state:
        st.session_state[f"{user_id}_show_month"] = today.month
    if f"{user_id}_last_click" not in st.session_state:
        st.session_state[f"{user_id}_last_click"] = 0.0

    now = time.time()
    last_click = st.session_state[f"{user_id}_last_click"]
    can_click = now - last_click > 0.5  # 防抖：0.5 秒

    year = st.session_state[f"{user_id}_show_year"]
    month = st.session_state[f"{user_id}_show_month"]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 上一個月", key=f"prev_show_{user_id}") and can_click:
            st.session_state[f"{user_id}_last_click"] = now
            if month == 1:
                st.session_state[f"{user_id}_show_month"] = 12
                st.session_state[f"{user_id}_show_year"] -= 1
            else:
                st.session_state[f"{user_id}_show_month"] -= 1
    with col3:
        if st.button("下一個月 →", key=f"next_show_{user_id}") and can_click:
            st.session_state[f"{user_id}_last_click"] = now
            if month == 12:
                st.session_state[f"{user_id}_show_month"] = 1
                st.session_state[f"{user_id}_show_year"] += 1
            else:
                st.session_state[f"{user_id}_show_month"] += 1

    # 讀取資料並繪製日曆
    df = get_df()
    user_data = df[df["user_id"] == user_id]
    if user_data.empty:
        st.warning(f"{user_id} 無資料")
        return

    available = set(d.strip() for d in user_data.iloc[0]['available_dates'].split(',') if d.strip())
    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdays(year, month))

    week_headers = ['一', '二', '三', '四', '五', '六', '日']
    table = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
    table += f"<caption style='text-align:center; font-weight:bold; padding: 8px'>{year} 年 {month} 月</caption>"
    table += "<tr>" + "".join(f"<th>{d}</th>" for d in week_headers) + "</tr><tr>"

    day_counter = 0
    for day in month_days:
        if day == 0:
            table += "<td></td>"
        else:
            date_str = f"{year}-{month:02d}-{day:02d}"
            if date_str in available:
                table += f"<td style='background-color:#b2fab4;border:1px solid #ccc;padding:5px'>{day}</td>"
            else:
                table += f"<td style='border:1px solid #ccc;padding:5px;color:#ccc'>{day}</td>"
        day_counter += 1
        if day_counter % 7 == 0:
            table += "</tr><tr>"
    table += "</tr></table>"

    st.markdown(table, unsafe_allow_html=True)

