import calendar
import streamlit as st
from datetime import datetime, timedelta

def date_selector_calendar(user_id):
    if f"{user_id}_edit_dates" not in st.session_state:
        st.session_state[f"{user_id}_edit_dates"] = set()

    if f"{user_id}_calendar_month" not in st.session_state:
        today = datetime.today()
        st.session_state[f"{user_id}_calendar_month"] = today.month
        st.session_state[f"{user_id}_calendar_year"] = today.year

    year = st.session_state[f"{user_id}_calendar_year"]
    month = st.session_state[f"{user_id}_calendar_month"]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 上一個月", key=f"prev_month_{user_id}"):
            if month == 1:
                st.session_state[f"{user_id}_calendar_month"] = 12
                st.session_state[f"{user_id}_calendar_year"] -= 1
            else:
                st.session_state[f"{user_id}_calendar_month"] -= 1
    with col3:
        if st.button("下一個月 →", key=f"next_month_{user_id}"):
            if month == 12:
                st.session_state[f"{user_id}_calendar_month"] = 1
                st.session_state[f"{user_id}_calendar_year"] += 1
            else:
                st.session_state[f"{user_id}_calendar_month"] += 1

    cal = calendar.Calendar(firstweekday=0)
    days = list(cal.itermonthdates(year, month))

    week_headers = ['一', '二', '三', '四', '五', '六', '日']
    st.markdown(f"### {year} 年 {month} 月 可用日期選擇")
    html = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
    html += "<tr>" + "".join([f"<th>{day}</th>" for day in week_headers]) + "</tr><tr>"

    day_count = 0
    for d in days:
        date_str = d.strftime("%Y-%m-%d")
        is_this_month = d.month == month
        selected = date_str in st.session_state[f"{user_id}_edit_dates"]

        if not is_this_month:
            html += "<td></td>"
        else:
            if st.button(str(d.day), key=f"{user_id}_{date_str}"):
                if selected:
                    st.session_state[f"{user_id}_edit_dates"].remove(date_str)
                else:
                    st.session_state[f"{user_id}_edit_dates"].add(date_str)

            style = "background-color:#b2fab4;" if selected else "color:#ccc;"
            html += f"<td style='border:1px solid #ccc; padding:5px; {style}'>{d.day}</td>"

        day_count += 1
        if day_count % 7 == 0:
            html += "</tr><tr>"
    html += "</tr></table>"

    st.markdown(html, unsafe_allow_html=True)
    st.info(f"已選擇日期：{sorted(st.session_state[f'{user_id}_edit_dates'])}")
