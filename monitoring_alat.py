import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

# Load API Key dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Ambil SEMUA data tanpa batas range
URL = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/A:Z?key={API_KEY}"

# Fungsi untuk mengambil data dari Google Sheets
@st.cache_data
def get_data():
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json().get("values", [])
        df = pd.DataFrame(data[1:], columns=data[0])  # Baris pertama sebagai header
        return df
    else:
        return pd.DataFrame()

# Ambil data
df = get_data()

# Sidebar menu
st.sidebar.title("📌 Menu Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Home", "Data", "Grafik", "Tentang"])

# Halaman Home
if menu == "Home":
    st.title("🏠 Home")
    st.write("Selamat datang di Dashboard!")

# Halaman Data
elif menu == "Data":
    st.title("📊 Data dari Google Sheets")
    if not df.empty:
        st.dataframe(df)
    else:
        st.error("Gagal mengambil data dari Google Sheets.")

# Halaman Grafik
elif menu == "Grafik":
    st.title("📈 Grafik Data")
    if not df.empty:
        try:
            df["Value"] = pd.to_numeric(df["Value"])  # Sesuaikan dengan nama kolom di Sheets
            fig = px.line(df, x="Date", y="Value", title="Grafik Data dari Google Sheets")
            st.plotly_chart(fig)
        except KeyError:
            st.error("Pastikan kolom 'Date' dan 'Value' ada dalam Google Sheets.")
    else:
        st.error("Tidak ada data untuk ditampilkan.")

# Halaman Tentang
elif menu == "Tentang":
    st.title("ℹ️ Tentang")
    st.write("Aplikasi ini dibuat untuk menampilkan data dari Google Sheets ke dalam dashboard menggunakan Streamlit.")
