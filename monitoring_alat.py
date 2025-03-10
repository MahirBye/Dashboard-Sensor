import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

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
        df = pd.DataFrame(data[1:], columns=data[0])
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

# Tampilkan judul dan deskripsi
st.title("📊 Dashboard Monitoring Real-Time")
st.markdown("### Data real-time penggunaan alat laboratorium")

# Tampilkan metric/gauge untuk data real-time
if not df.empty:
    latest_data = df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    st.write(latest_data)

    with col1:
        st.metric(label="⚡ Tegangan (V)", value=latest_data["Voltage"])
    with col2:
        st.metric(label="💡 Arus (A)", value=latest_data["Current"])
    with col3:
        st.metric(label="🔋 Daya Aktif (W)", value=latest_data["Activepower"])

    style_metric_cards(border_color="#4CAF50", background_color="#E8F5E9", border_radius_px=10)

# Tampilkan tabel data
st.markdown("### Tabel Data")
st.dataframe(df, use_container_width=True)

# Visualisasi grafik
if not df.empty:
    numeric_columns = df.select_dtypes(include=['object']).columns
    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    all_columns = df.columns.tolist()
    x_axis = st.selectbox("Pilih X-Axis:", all_columns)
    y_axis = st.selectbox("Pilih Y-Axis:", all_columns)

    if x_axis and y_axis:
        fig = px.line(df, x=x_axis, y=y_axis, title=f"Grafik {y_axis} vs {x_axis}", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Pilih kolom untuk visualisasi.")
