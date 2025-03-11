import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import plotly.express as px

st.set_page_config(
    page_title="Real-Time Monitoring Dashboard",
    page_icon="⚡",
    layout="wide",
)

# Load variabel dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# URL untuk mendapatkan daftar sheet
SHEET_METADATA_URL = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}?key={API_KEY}"

# Fungsi untuk mengambil data dari Google Sheets
@st.cache_data
def get_data(sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{sheet_name}?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("values", [])
        df = pd.DataFrame(data[1:], columns=data[0])  # Gunakan baris pertama sebagai header
        return df
    else:
        st.error(f"Gagal mengambil data dari sheet: {sheet_name}")
        return pd.DataFrame()

# Ambil semua sheet
response = requests.get(SHEET_METADATA_URL)
sheets = [sheet["properties"]["title"] for sheet in response.json().get("sheets", [])]

# Pilih sheet yang akan ditampilkan
selected_sheet = st.sidebar.selectbox("Pilih Sheet", sheets)

# Placeholder untuk data dan visualisasi
placeholder = st.empty()

df = get_data(selected_sheet)

with placeholder.container():
    # Dashboard title
    st.title("⚡ Real-Time Monitoring Data Pemakaian Alat Laboratorium")

    # Pilihan kolom untuk visualisasi
    if not df.empty:
        # Konversi kolom numerik
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass

        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

        selected_columns = st.multiselect("📊 Pilih Kolom untuk Time Series:", numeric_columns, default=numeric_columns[:2])

        if len(selected_columns) >= 2:
            st.markdown(f"### ⏳ Time Series {selected_columns[1]} vs {selected_columns[0]}")
            fig = px.line(df, x=selected_columns[0], y=selected_columns[1:])
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📝 Data Lengkap")
        st.dataframe(df)
