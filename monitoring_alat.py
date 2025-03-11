import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

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
        if data:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
    return pd.DataFrame()

# UI dengan Streamlit
st.title("Dashboard Data Google Sheets")

# Pilih sheet
sheet_name = st.text_input("Masukkan nama sheet:", "Sheet1")

# Ambil data
if sheet_name:
    df = fetch_data(sheet_name)
    if not df.empty:
        st.write("### Data")
        st.write(df)

        # Tambahkan pencarian
        search_query = st.text_input("Cari data:")
        if search_query:
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
            st.write("### Hasil Pencarian")
            st.write(filtered_df)

        # Konversi kolom pertama menjadi datetime jika memungkinkan
        try:
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
            df = df.sort_values(by=df.columns[0])
            st.write("### Time Series")
            fig = px.line(df, x=df.columns[0], y=df.columns[1:], title="Time Series Data")
            st.plotly_chart(fig)
        except Exception as e:
            st.warning("Tidak bisa menampilkan grafik time series. Pastikan kolom pertama adalah tanggal.")

        # Grafik tambahan (misalnya bar chart)
        numeric_columns = df.select_dtypes(include=['number']).columns
        if not numeric_columns.empty:
            st.write("### Grafik Data")
            fig_bar = px.bar(df, x=df.columns[0], y=numeric_columns, title="Bar Chart Data")
            st.plotly_chart(fig_bar)
    else:
        st.warning("Data tidak ditemukan. Periksa nama sheet.")
