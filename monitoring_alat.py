import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load API Key dari .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

def fetch_sheets():
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        sheets = response.json().get("sheets", [])
        return [sheet["properties"]["title"] for sheet in sheets]
    return []

def fetch_data(sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{sheet_name}?key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("values", [])
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    return pd.DataFrame()

# Streamlit UI
st.title("Dashboard Monitoring Google Sheets")

# Pilih Sheet
sheets = fetch_sheets()
selected_sheet = st.selectbox("Pilih Sheet:", sheets)

data = fetch_data(selected_sheet)
if not data.empty:
    # Pilih alat
    alat_list = data['Alat'].unique().tolist()
    selected_alat = st.selectbox("Pilih Alat:", alat_list)
    
    # Filter data berdasarkan alat
    filtered_data = data[data['Alat'] == selected_alat]
    st.write("### Data Terpilih")
    st.dataframe(filtered_data)
    
    # Konversi kolom waktu ke datetime
    if 'Waktu' in filtered_data.columns:
        filtered_data['Waktu'] = pd.to_datetime(filtered_data['Waktu'])
        
        # Time Series
        st.line_chart(filtered_data.set_index('Waktu')['Nilai'])
        
        # Grafik lainnya
        st.bar_chart(filtered_data.set_index('Waktu')['Nilai'])