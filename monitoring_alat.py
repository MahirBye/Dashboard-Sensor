import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv
import os

# Load API Key dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Fungsi untuk mengambil data dari Google Sheets
def fetch_data(sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{sheet_name}?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("values", [])
        df = pd.DataFrame(data[1:], columns=data[0])  # Gunakan baris pertama sebagai header
        return df
    return pd.DataFrame()

# Ambil data dari sheet utama
df = fetch_data("Sheet1")  # Ganti dengan nama sheet yang sesuai

# Pastikan ada data sebelum melanjutkan
if not df.empty:
    st.title("Dashboard Monitoring")
    
    # Kolom pencarian alat
    alat_list = df["Alat"].unique().tolist()
    selected_alat = st.selectbox("Pilih Alat:", alat_list)
    
    # Filter data berdasarkan alat yang dipilih
    filtered_df = df[df["Alat"] == selected_alat]
    st.write("Data untuk alat yang dipilih:")
    st.dataframe(filtered_df)
    
    # Pastikan ada data yang sesuai sebelum menampilkan grafik
    if not filtered_df.empty:
        # Ubah kolom waktu menjadi datetime jika ada
        if "Waktu" in filtered_df.columns:
            filtered_df["Waktu"] = pd.to_datetime(filtered_df["Waktu"])
            
            # Grafik Time Series
            fig = px.line(filtered_df, x="Waktu", y="Hasil", title=f"Time Series Data {selected_alat}")
            st.plotly_chart(fig)
        
        # Grafik tambahan (misalnya distribusi nilai)
        fig2 = px.histogram(filtered_df, x="Hasil", title="Distribusi Hasil")
        st.plotly_chart(fig2)
else:
    st.write("Tidak ada data yang tersedia.")
