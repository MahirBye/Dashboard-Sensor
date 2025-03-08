import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # Untuk grafik interaktif

# Google Sheets Config
SPREADSHEET_ID = '1RTnFf8zNOUbh-rdfUn64U-5LncqH2HQL2sgZ_vRgtKg'  # Ganti dengan ID Google Sheets kamu
API_KEY = 'AIzaSyDFiT5r_Th2gQ6PvqGljDHfrqanar5y940'  # Ganti dengan API Key kamu

# Fungsi untuk mendapatkan daftar sheet
def get_sheets():
    url = f"https://sheets.googleapis.com/v4/spreadsheets/1RTnFf8zNOUbh-rdfUn64U-5LncqH2HQL2sgZ_vRgtKg?key=AIzaSyDFiT5r_Th2gQ6PvqGljDHfrqanar5y940"
    response = requests.get(url)
    sheets_info = response.json()
    
    if "sheets" in sheets_info:
        return [sheet['properties']['title'] for sheet in sheets_info['sheets']]
    return []

# Fungsi untuk mendapatkan data dari sheet tertentu
def get_sheet_data(sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/1RTnFf8zNOUbh-rdfUn64U-5LncqH2HQL2sgZ_vRgtKg/values/{sheet_name}?key=AIzaSyDFiT5r_Th2gQ6PvqGljDHfrqanar5y940"
    response = requests.get(url)
    data = response.json()

    if 'values' in data:
        df = pd.DataFrame(data['values'][1:], columns=data['values'][0])
        return df
    return pd.DataFrame()

# Streamlit UI
st.title("📊 Google Sheets Dashboard dengan Streamlit")

# Ambil daftar sheet
sheets = get_sheets()
selected_sheet = st.selectbox("Pilih Sheet:", sheets)

# Tampilkan data dari sheet yang dipilih
if selected_sheet:
    df = get_sheet_data(selected_sheet)

    if not df.empty:
        st.write(f"### Data dari Sheet: {selected_sheet}")
        st.dataframe(df)

        # Konversi kolom angka
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        # Pilih kolom untuk grafik
        all_columns = df.columns.tolist()
        x_axis = st.selectbox("Pilih X-Axis:", all_columns)
        y_axis = st.selectbox("Pilih Y-Axis:", all_columns)

        # Buat grafik
        if x_axis and y_axis:
            fig = px.line(df, x=x_axis, y=y_axis, title=f"Grafik {y_axis} vs {x_axis}")
            st.plotly_chart(fig)
    else:
        st.warning("Data tidak ditemukan di sheet ini.")
