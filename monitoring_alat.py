import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import plotly.express as px

# Load variabel dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# URL untuk mendapatkan daftar sheet
SHEET_METADATA_URL = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}?key={API_KEY}"

# Fungsi untuk mendapatkan daftar sheet
def get_sheets():
    response = requests.get(SHEET_METADATA_URL)
    if response.status_code == 200:
        sheets = response.json().get("sheets", [])
        return [sheet["properties"]["title"] for sheet in sheets]
    else:
        st.error("Gagal mengambil daftar sheet")
        return []

# Fungsi untuk mengambil data dari satu sheet
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
sheets = get_sheets()

# Sidebar dengan style
st.sidebar.title("📂 Pilihan Sheet")
st.sidebar.markdown("Pilih sheet untuk menampilkan data dan visualisasi")

# Pilih sheet yang akan ditampilkan
selected_sheet = st.sidebar.selectbox("Pilih Sheet", sheets)

# Ambil data dari sheet yang dipilih
df = get_data(selected_sheet)

# Tampilkan data dengan style yang lebih menarik
st.title("📊 Dashboard Data Google Sheets")
st.markdown(f"### Menampilkan data dari sheet: **{selected_sheet}**")

if not df.empty:
    st.dataframe(df.style.set_table_styles(
        [{'selector': 'thead th', 'props': [('background-color', '#4CAF50'), ('color', 'white')]}]
    ))

    # Pilih kolom untuk grafik
    all_columns = df.columns.tolist()
    x_axis = st.selectbox("🧩 Pilih X-Axis:", all_columns)
    y_axis = st.selectbox("📈 Pilih Y-Axis:", all_columns)

    if x_axis and y_axis:
        fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", markers=True)
        st.plotly_chart(fig)

    st.markdown("---")
    st.info("🔍 Gunakan sidebar untuk mengganti sheet dan melihat data lain.")
else:
    st.warning("⚠️ Data tidak ditemukan di sheet ini.")
