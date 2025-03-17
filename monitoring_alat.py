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
print(response.json())

# Pilih sheet yang akan ditampilkan
selected_sheet = st.sidebar.selectbox("Pilih Sheet", sheets)

# Placeholder untuk data dan visualisasi
df = get_data(selected_sheet)

if not df.empty:
    # Konversi kolom numerik
    for col in ["Tegangan (V)", "Arus (A)", "Daya Aktif (W)", "Energi Aktif (Wh)", "Frekuensi (Hz)", "Faktor Daya", "Daya Reaktif (VAR)", "Daya Semu (VA)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Konversi waktu ke format datetime
    if "Waktu" in df.columns:
        df["Waktu"] = pd.to_datetime(df["Waktu"], format="%H:%M:%S", errors='coerce')

    st.title("📊 Dashboard Analisis Data Sensor")
    
    # *1. Menampilkan Tabel Data*
    st.write("### Data Sensor")
    st.data_editor(df.drop(columns=["ID"], errors='ignore'), hide_index=True)
    
    # *2. Statistik Data*
    st.write("### Statistik Data")
    st.write(df.describe())

    # *3. Grafik Time Series*
    st.write("### Grafik Time Series")
    selected_columns = st.multiselect("Pilih data untuk ditampilkan:", df.select_dtypes(include=["number"]).columns.tolist(), default=["Tegangan (V)"])
    if selected_columns:
        st.line_chart(df.set_index("Waktu")[selected_columns])
    else:
        st.warning("Pilih minimal satu parameter untuk ditampilkan di grafik.")

    # *4. Pencarian dan Filter Data*
    st.write("### Pencarian Data")
    search_query = st.text_input("🔎 Cari berdasarkan Nama Alat:", "")
    filtered_df = df[df["Nama Alat"].str.contains(search_query, case=False, na=False)]
    st.data_editor(filtered_df.drop(columns=["ID"], errors='ignore'), hide_index=True, key="filtered_table")
    
    # *5. Heatmap Korelasi Antar Variabel*
    st.write("### Korelasi Antar Parameter")
    fig, ax = plt.subplots()
    sns.heatmap(df.select_dtypes(include=["number"]).corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
    
    # *6. Deteksi Anomali Data*
    df["Anomali"] = (df["Tegangan (V)"] < 210) | (df["Tegangan (V)"] > 230) | (df["Arus (A)"] < 0.025) | (df["Arus (A)"] > 0.045)
    anomali_df = df[df["Anomali"]]
    if not anomali_df.empty:
        st.warning("⚠ Ditemukan data anomali!")
        st.dataframe(anomali_df)
    else:
        st.success("✅ Tidak ada anomali dalam data.")
    
    # *7. Histogram Distribusi Tegangan & Arus*
    st.write("### Histogram Tegangan & Arus")
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    sns.histplot(df["Tegangan (V)"], bins=10, kde=True, ax=ax[0])
    ax[0].set_title("Distribusi Tegangan (V)")
    sns.histplot(df["Arus (A)"], bins=10, kde=True, ax=ax[1])
    ax[1].set_title("Distribusi Arus (A)")
    st.pyplot(fig)
