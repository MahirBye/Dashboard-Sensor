import time
import numpy as np
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
@st.experimental_memo
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

# Ambil data dari sheet yang dipilih
df = get_data(selected_sheet)

# Dashboard title
st.title("⚡ Real-Time Monitoring Data Pemakaian Alat Laboratorium")

# Simulasi data real-time
for seconds in range(200):
    if not df.empty:
        df["Tegangan (V)"] = pd.to_numeric(df["Tegangan (V)"], errors='coerce')
        df["Arus (A)"] = pd.to_numeric(df["Arus (A)"], errors='coerce')
        df["Daya Aktif (W)"] = pd.to_numeric(df["Daya Aktif (W)"], errors='coerce')

        avg_voltage = np.mean(df["Tegangan (V)"])
        avg_current = np.mean(df["Arus (A)"])
        avg_power = np.mean(df["Daya Aktif (W)"])

        with st.empty().container():
            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                label="⚡ Rata-rata Tegangan (V)",
                value=round(avg_voltage, 2),
                delta=round(avg_voltage) - 220,
            )

            kpi2.metric(
                label="💡 Rata-rata Arus (A)",
                value=round(avg_current, 2),
                delta=round(avg_current) - 2,
            )

            kpi3.metric(
                label="🔋 Rata-rata Daya Aktif (W)",
                value=round(avg_power, 2),
                delta=round(avg_power) - 60,
            )

            fig_col1, fig_col2 = st.columns(2)
            with fig_col1:
                st.markdown("### 🔥 Heatmap Tegangan vs Arus")
                fig = px.density_heatmap(data_frame=df, y="Tegangan (V)", x="Arus (A)")
                st.write(fig)

            with fig_col2:
                st.markdown("### 📊 Histogram Daya Aktif")
                fig2 = px.histogram(data_frame=df, x="Daya Aktif (W)")
                st.write(fig2)

            st.markdown("### 📝 Data Lengkap")
            st.dataframe(df)
            time.sleep(1)