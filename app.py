
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import time
import json


st.set_page_config(page_title="Mood of the Queue", page_icon="📈")
st.title("🧪 Mood of the Queue")
st.markdown("Log your mood and view trends throughout the day.")

@st.cache_resource
def get_worksheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)

    spreadsheet = client.create("New Mood Tracker")
    spreadsheet.share("srnparisa@gmail.com", perm_type="user", role="writer")
    sheet = spreadsheet.sheet1

    print("New sheet created and shared.")
    sheet.append_row(["timestamp", "mood", "note"])
    print("🔗 Sheet URL:", spreadsheet.url)
    st.markdown(f"🔗 [Open Google Sheet]({spreadsheet.url})", unsafe_allow_html=True)
    
    return sheet

sheet = get_worksheet()

@st.cache_data(ttl=60)
def load_data():
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if df.empty or "timestamp" not in df.columns:
        return pd.DataFrame(columns=["timestamp", "mood", "note", "date"])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    return df

data = load_data()
print(data)

st.subheader("📊 Mood Trends")

if not data.empty:
    with st.expander("🔍 Filter Options", expanded=True):
        date_option = st.radio("View by:", ["Today", "Select a Date", "All Dates"], horizontal=True)

    if date_option == "Today":
        filtered = data[data["date"] == date.today()]
        title = f"Mood Count for Today ({date.today().strftime('%b %d')})"
    elif date_option == "Select a Date":
        unique_dates = sorted(data["date"].unique(), reverse=True)
        selected_date = st.selectbox("Pick a date", unique_dates)
        filtered = data[data["date"] == selected_date]
        title = f"Mood Count for {selected_date.strftime('%b %d, %Y')}"
    else:
        filtered = data
        title = "Mood Count (All Dates Combined)"

    if not filtered.empty:
        mood_counts = filtered["mood"].value_counts().reset_index()
        mood_counts.columns = ["mood", "count"]

        fig = px.bar(
            mood_counts,
            x="mood",
            y="count",
            title=title,
            labels={"count": "Entries", "mood": "Mood"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No mood data found for the selected range.")
else:
    st.info("No mood data found yet.")


'''
st.subheader("2️⃣ Mood Trends")

if not data.empty:
    today = date.today()
    filtered = data[data["date"] == today]


    if not filtered.empty:
        mood_counts = filtered["mood"].value_counts().reset_index()
        mood_counts.columns = ["mood", "count"]
        fig = px.bar(
            mood_counts,
            x="mood",
            y="count",
            title=f"Mood Count for {today.strftime('%B %d, %Y')}",
            labels={"count": "Entries", "mood": "Mood"},
        )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No moods logged today yet.")
'''
st.caption("⏱ Auto-refresh every 30 seconds")
time.sleep(30)
st.rerun()
