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

# Pilih sheet yang akan ditampilkan
selected_sheet = st.sidebar.selectbox("Pilih Sheet", sheets)

# Ambil data dari sheet yang dipilih
df = get_data(selected_sheet)

# Tampilkan data
st.title("📊 Dashboard Data Google Sheets")
st.write(f"Menampilkan data dari sheet: **{selected_sheet}**")
st.dataframe(df)

# Buat Grafik (jika data cukup)
if not df.empty:
    if len(df.columns) >= 2:
        col1, col2 = df.columns[:2]  # Ambil 2 kolom pertama sebagai contoh
        df[col2] = pd.to_numeric(df[col2], errors="coerce")  # Pastikan kolom angka dalam format numerik
        fig = px.line(df, x=col1, y=col2, title=f"Grafik {col2} berdasarkan {col1}")
        st.plotly_chart(fig)
    else:
        st.warning("Data tidak cukup untuk membuat grafik.")
else:
    st.error("Data tidak tersedia.")
