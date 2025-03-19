import os
import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from dotenv import load_dotenv

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

# Header dengan Link
st.markdown("""
    <h1 style='text-align: center; color: brown;'>Real-Time Monitoring</h1>
    <p style='text-align: center;'>
    </p>
""", unsafe_allow_html=True)

# Sidebar untuk memilih sheet
selected_sheet = st.sidebar.selectbox("Pilih Sheet", sheets)
df = get_data(selected_sheet)

# Tombol Navigasi
col1, col2 = st.columns([1, 1])
with col1:
    show_data = st.button("DATA", key="show_data")
with col2:
    show_graph = st.button("GRAFIK", key="show_graph")

if not df.empty:
    # Konversi kolom numerik
    for col in ["Tegangan (V)", "Arus (A)", "Daya Aktif (W)", "Energi Aktif (Wh)", "Frekuensi (Hz)", "Faktor Daya", "Daya Reaktif (VAR)", "Daya Semu (VA)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Konversi waktu ke format datetime
    if "Waktu" in df.columns:
        df["Waktu"] = pd.to_datetime(df["Waktu"], format="%H:%M:%S", errors='coerce')
    
    if show_data:
        st.write("### Data Sensor")
        st.data_editor(df.drop(columns=["ID"], errors='ignore'), hide_index=True)
        st.write("### Statistik Data")
        st.write(df.describe())
    
    if show_graph:
        st.write("### Grafik Time Series")
        selected_columns = st.multiselect("Pilih data untuk ditampilkan:", df.select_dtypes(include=["number"]).columns.tolist(), default=["Tegangan (V)"])
        if selected_columns:
            st.line_chart(df.set_index("Waktu")[selected_columns])
        else:
            st.warning("Pilih minimal satu parameter untuk ditampilkan di grafik.")
        
        st.write("### Korelasi Antar Parameter")
        fig, ax = plt.subplots()
        sns.heatmap(df.select_dtypes(include=["number"]).corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
