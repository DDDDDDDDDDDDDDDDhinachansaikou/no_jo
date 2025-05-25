
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sheets import get_df

def display_user_calendar(user_id):
    df = get_df()
    user_data = df[df['user_id'] == user_id]
    if user_data.empty:
        st.warning(f"{user_id} 無資料")
        return

    dates = user_data.iloc[0]['available_dates']
    available_set = set(d.strip() for d in dates.split(',') if d.strip())

    today = datetime.today()
    next_30_days = [today + timedelta(days=i) for i in range(30)]
    date_labels = [d.strftime("%Y-%m-%d") for d in next_30_days]

    calendar_df = pd.DataFrame({
        "日期": date_labels,
        "可用": ["是" if d in available_set else "否" for d in date_labels]
    })
    st.table(calendar_df)

    fig = go.Figure(go.Bar(
        x=date_labels,
        y=[1 if d in available_set else 0 for d in date_labels],
        marker_color=["green" if d in available_set else "lightgray" for d in date_labels],
    ))
    fig.update_layout(
        title=f"{user_id} 的未來可用日",
        xaxis_title="日期",
        yaxis=dict(showticklabels=False),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
