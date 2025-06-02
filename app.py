
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

    print("✅ New sheet created and shared.")
    print("🔗 Sheet URL:", spreadsheet.url)
    st.markdown(f"🔗 [Open Google Sheet]({spreadsheet.url})", unsafe_allow_html=True)
    
    return sheet

sheet = get_worksheet()

st.subheader("1️⃣ Log a Mood")
with st.form("mood_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        mood = st.selectbox("Mood", ["😊", "😠", "😕", "🎉"], index=0)
    with col2:
        note = st.text_input("Optional note")
    submitted = st.form_submit_button("Submit Mood")
    if submitted:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, mood, note])
        st.success("✅ Mood logged!")

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
            title=f"Mood Count for {selected_date}",
            labels={"count": "Entries", "mood": "Mood"},
        )
        fig.update_layout(xaxis_title="Mood", yaxis_title="Count", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No moods logged for the selected date.")
else:
    st.info("No mood data found yet.")

