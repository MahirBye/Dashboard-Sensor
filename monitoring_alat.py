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

# Ambil data dari sheet yang dipilih
df = get_data(selected_sheet)

# Dashboard title
st.title("⚡ Real-Time Monitoring Data Pemakaian Alat Laboratorium")

# Pilihan kolom untuk visualisasi
if not df.empty:
    numeric_columns = df.select_dtypes(include=['object']).columns
    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    all_columns = df.columns.tolist()
    x_axis = st.selectbox("📈 Pilih X-Axis:", all_columns)
    y_axis = st.selectbox("📉 Pilih Y-Axis:", all_columns)

    # Pilihan visualisasi
    visualization_option = st.selectbox("Pilih Visualisasi", ["Heatmap", "Histogram"])

    for _ in range(200):
        avg_x = np.mean(df[x_axis])
        avg_y = np.mean(df[y_axis])

        with st.empty().container():
            kpi1, kpi2 = st.columns(2)

            kpi1.metric(
                label=f"📊 Rata-rata {x_axis}",
                value=round(avg_x, 2),
                delta=round(avg_x) - round(avg_x * 0.1),
            )

            kpi2.metric(
                label=f"📊 Rata-rata {y_axis}",
                value=round(avg_y, 2),
                delta=round(avg_y) - round(avg_y * 0.1),
            )

            if visualization_option == "Heatmap":
                st.markdown(f"### 🔥 Heatmap {y_axis} vs {x_axis}")
                fig = px.density_heatmap(data_frame=df, x=x_axis, y=y_axis)
                st.plotly_chart(fig, use_container_width=True)
            elif visualization_option == "Histogram":
                st.markdown(f"### 📊 Histogram {y_axis}")
                fig2 = px.histogram(data_frame=df, x=y_axis)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### 📝 Data Lengkap")
            st.dataframe(df)

        time.sleep(1)
