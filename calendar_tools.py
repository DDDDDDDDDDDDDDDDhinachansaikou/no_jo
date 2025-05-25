
import calendar
from datetime import datetime, timedelta, date
import streamlit as st
from sheets import get_df

# ✅ 用於「選擇」可用日期：顯示並點選選取
def select_date_calendar(user_id):
    df = get_df()
    user_data = df[df["user_id"] == user_id]
    if user_data.empty:
        st.warning("找不到使用者資料")
        return

    today = date.today()
    selected_dates = st.multiselect("請選擇可用日期", 
        options=[today + timedelta(days=i) for i in range(30)],
        format_func=lambda d: d.strftime("%Y-%m-%d"),
        default=[]
    )

    selected_strs = [d.strftime("%Y-%m-%d") for d in selected_dates]
    if st.button("儲存可用日期"):
        df.loc[df["user_id"] == user_id, "available_dates"] = ",".join(selected_strs)
        from sheets import save_df
        save_df(df)
        st.success("已儲存可用日期")
    return selected_strs

# ✅ 用於顯示某人可用日期：不可互動
def display_calendar_view(user_id):
    df = get_df()
    user_data = df[df["user_id"] == user_id]
    if user_data.empty:
        st.warning(f"{user_id} 無資料")
        return

    today = datetime.today()
    year = today.year
    month = today.month
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
