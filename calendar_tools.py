
import calendar
from datetime import datetime
import streamlit as st
from sheets import get_df

def render_user_month_calendar(user_id):
    df = get_df()
    user_data = df[df['user_id'] == user_id]
    if user_data.empty:
        st.warning(f"{user_id} 無資料")
        return

    today = datetime.today()
    year = today.year
    month = today.month

    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdays(year, month))

    available = set(d.strip() for d in user_data.iloc[0]['available_dates'].split(',') if d.strip())

    week_headers = ['一', '二', '三', '四', '五', '六', '日']
    table = "<table style='border-collapse: collapse; width: 100%; text-align: center;'>"
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
    st.markdown(f"#### {user_id} 的 {year}年{month}月 空閒日曆")
    st.markdown(table, unsafe_allow_html=True)
