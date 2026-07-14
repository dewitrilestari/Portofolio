import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# ==============================================================================
# 1. KONFIGURASI HALAMAN & STYLE
# ==============================================================================
st.set_page_config(page_title="Dashboard Forecasting Curah Hujan LSTM", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
    .metric-box { padding: 15px; background-color: #F3F4F6; border-radius: 8px; text-align: center; box-shadow: 1px 1px 5px rgba(0,0,0,0.05); }
    .metric-val { font-size: 24px; font-weight: bold; color: #1D4ED8; }
    .metric-lbl { font-size: 14px; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌧️ Aplikasi Forecasting Curah Hujan (RR) - LSTM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Platform interaktif untuk memprediksi curah hujan harian dan mengevaluasi performa model Deep Learning LSTM.</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. MEMUAT DATA HISTORIS & MODEL ASLI (.keras)
# ==============================================================================
# Mendapatkan direktori tempat file app.py ini berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_my_lstm_model():
    # Menggabungkan folder app.py dengan nama file model
    model_path = os.path.join(BASE_DIR, 'model_lstm.h5')
    return load_model(model_path)

@st.cache_data
def load_historical_data():
    # Menggabungkan folder app.py dengan nama file dataset CSV Anda
    # Ganti 'data_curah_hujan.csv' sesuai nama file asli Anda
    data_path = os.path.join(BASE_DIR, 'Juli 2024 - Juli 2026.xlsx')
    df = pd.read_excel(data_path)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    return df

# Memanggil fungsi load
try:
    model_lstm = load_my_lstm_model()
    df_filtered = load_historical_data()
    model_loaded = True
except Exception as e:
    st.error(f"Gagal memuat model atau data: {e}")
    st.info("Pastikan file 'model_lstm.h5' dan dataset csv Anda sudah berada di direktori yang sama.")
    model_loaded = False

# Nilai evaluasi statis dari hasil training sebelumnya
metrics_data = {
    'MAE': 6.627,
    'RMSE': 12.857,
    'MAPE': 162.595
}

if model_loaded:
    # ==============================================================================
    # 3. SIDEBAR / PANEL KONTROL
    # ==============================================================================
    st.sidebar.header("🎛️ Panel Kontrol")
    
    # Fitur 1: Memilih Horizon Forecasting
    horizon = st.sidebar.selectbox(
        "Pilih Horizon Forecasting (Hari):",
        options=[7, 14, 30],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Informasi Model:**
    * **Arsitektur:** LSTM (Deep Learning)
    * **Target Variabel:** Curah Hujan (RR) dalam satuan mm
    * **Format File:** Native Keras (.keras)
    """)
    
    # ==============================================================================
    # 4. GRID METRIK EVALUASI MODEL
    # ==============================================================================
    st.subheader("📊 Metrik Evaluasi Model (Data Uji)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{metrics_data["MAE"]} mm</div><div class="metric-lbl">MAE (Mean Absolute Error)</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{metrics_data["RMSE"]} mm</div><div class="metric-lbl">RMSE (Root Mean Squared Error)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{metrics_data["MAPE"]:.3f} %</div><div class="metric-lbl">MAPE (Mean Absolute Percentage Error)</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==============================================================================
    # 5. PROSES FORECASTING REKURSIF (RIIL DARI MODEL LSTM)
    # ==============================================================================
    # Menyiapkan fitur terakhir yang berskala (scaled) dari data untuk input awal LSTM
    # Catatan: Sesuaikan bagian ini jika Anda menyimpan objek scaler secara terpisah
    # Di sini diasumsikan data fitur terakhir diambil dari baris paling bontot di dataset
    
    # Contoh ekstraksi array fitur terakhir (sesuaikan jumlah kolom fitur Anda)
    fitur_kolom = [col for col in df_filtered.columns if col not in ['Tanggal', 'RR']]
    last_input = df_filtered[fitur_kolom].iloc[-1].values.copy()
    
    future_predictions = []
    current_input_3d = np.reshape(last_input, (1, 1, len(last_input)))
    
    for i in range(horizon):
        # Prediksi menggunakan model LSTM asli
        pred_1step = model_lstm.predict(current_input_3d, verbose=0).flatten()[0]
        pred_1step = max(0, pred_1step)  # Mengamankan agar curah hujan tidak bernilai negatif
        future_predictions.append(pred_1step)
        
        # Geser window fitur secara autoregressive
        new_input = np.roll(last_input, -1)
        new_input[-1] = pred_1step
        last_input = new_input
        current_input_3d = np.reshape(last_input, (1, 1, len(last_input)))
        
    # Membuat index tanggal masa depan berdasarkan tanggal terakhir di dataset
    last_date = pd.to_datetime(df_filtered['Tanggal'].iloc[-1])
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
    df_forecast = pd.DataFrame({'Tanggal': future_dates, 'Prediksi Curah Hujan (mm)': future_predictions})
    
    # ==============================================================================
    # 6. VISUALISASI GRAFIK (HISTORIS & FORECAST)
    # ==============================================================================
    st.subheader("📈 Visualisasi Data Aktual dan Hasil Forecast")
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Plot Data Historis Aktual (30 Hari Terakhir agar kontras)
    dates_actual = df_filtered['Tanggal'].iloc[-30:]
    y_actual = df_filtered['RR'].iloc[-30:]
    ax.plot(dates_actual, y_actual, label='Data Aktual (30 Hari Terakhir)', color='black', linewidth=2, marker='o', markersize=3)
    
    # Plot Data Hasil Forecast Masa Depan
    ax.plot(df_forecast['Tanggal'], df_forecast['Prediksi Curah Hujan (mm)'], 
            label=f'Forecast LSTM ({horizon} Hari)', color='red', linestyle='--', marker='o', markersize=5)
            
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Curah Hujan (mm)")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle='--', alpha=0.5)
    fig.autofmt_xdate()
    
    st.pyplot(fig)
    
    # ==============================================================================
    # 7. MENAMPILKAN NILAI PREDIKSI DALAM TABEL
    # ==============================================================================
    st.subheader(f"📋 Tabel Nilai Hasil Prediksi ({horizon} Hari ke Depan)")
    
    df_table = df_forecast.copy()
    df_table['Tanggal'] = df_table['Tanggal'].dt.strftime('%Y-%m-%d')
    df_table['Prediksi Curah Hujan (mm)'] = df_table['Prediksi Curah Hujan (mm)'].round(3)
    
    col_table, col_empty = st.columns([0.6, 0.4])
    with col_table:
        st.dataframe(df_table, use_container_width=True, hide_index=True)
