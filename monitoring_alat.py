import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load API Key dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Fungsi untuk mengambil daftar sheet
def get_sheets():
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        sheets = response.json().get("sheets", [])
        return [sheet["properties"]["title"] for sheet in sheets]
    return []

# Fungsi untuk mengambil data dari Google Sheets
def fetch_data(sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{sheet_name}?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("values", [])
        if data:
            df = pd.DataFrame(data[1:], columns=data[0])  # Gunakan baris pertama sebagai header
            return df
    return pd.DataFrame()

# Streamlit App
st.title("📊 Dashboard Monitoring Data")

# Pilih sheet
sheets = get_sheets()
selected_sheet = st.selectbox("Pilih Sheet:", sheets)

# Ambil data jika sheet dipilih
if selected_sheet:
    df = fetch_data(selected_sheet)
    
    if not df.empty:
        # Konversi tipe data
        df["Waktu"] = pd.to_datetime(df["Waktu"], format="%H:%M:%S", errors='coerce')
        numeric_columns = [col for col in df.columns if col not in ["ID", "Nama Alat", "Waktu"]]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        
        # Pilih alat
        alat_list = df["Nama Alat"].unique().tolist()
        selected_alat = st.selectbox("Pilih Alat:", alat_list)
        
        # Filter data berdasarkan alat
        filtered_df = df[df["Nama Alat"] == selected_alat]
        st.write("### Data Alat yang Dipilih")
        st.dataframe(filtered_df)
        
        # Grafik Time Series
        st.write("### Grafik Time Series")
        selected_columns = st.multiselect("Pilih data untuk ditampilkan:", numeric_columns, default=["Tegangan (V)"])
        if selected_columns:
            st.line_chart(filtered_df.set_index("Waktu")[selected_columns])
        
        # Korelasi antar parameter
        st.write("### Korelasi Antar Parameter")
        fig, ax = plt.subplots()
        sns.heatmap(filtered_df[numeric_columns].corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
        
        # Deteksi Anomali
        filtered_df["Anomali"] = (filtered_df["Tegangan (V)"] < 210) | (filtered_df["Tegangan (V)"] > 230)
        anomali_df = filtered_df[filtered_df["Anomali"]]
        if not anomali_df.empty:
            st.warning("⚠ Ditemukan data anomali!")
            st.dataframe(anomali_df)
        else:
            st.success("✅ Tidak ada anomali dalam data.")
        
        # Histogram Distribusi
        st.write("### Histogram Tegangan & Arus")
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        sns.histplot(filtered_df["Tegangan (V)"], bins=10, kde=True, ax=ax[0])
        ax[0].set_title("Distribusi Tegangan (V)")
        sns.histplot(filtered_df["Arus (A)"], bins=10, kde=True, ax=ax[1])
        ax[1].set_title("Distribusi Arus (A)")
        st.pyplot(fig)
    else:
        st.error("Data tidak tersedia atau terjadi kesalahan dalam pengambilan data.")