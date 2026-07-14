import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

# ====================================================================
# 1. MONKEY PATCHING UNTUK LAYER DENSE KERAS (SOLUSI MUTAKHIR)
# ====================================================================
# Kita memodifikasi metode deserialisasi Dense secara global sebelum memuat model.
import tensorflow as tf
from tensorflow.keras.layers import Dense

original_dense_from_config = Dense.from_config

def patched_dense_from_config(cls, config):
    # Hapus parameter bermasalah jika ada di dalam konfigurasi JSON model
    config.pop('quantization_config', None)
    return original_dense_from_config(config)

# Pasang patch ke class Dense bawaan Keras
Dense.from_config = classmethod(patched_dense_from_config)

from tensorflow.keras.models import load_model

# Mendapatkan direktori tempat file app.py berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ====================================================================
# 2. FUNGSI LOAD DATA, MODEL, & SCALER
# ====================================================================
@st.cache_resource
def load_my_lstm_model():
    model_path = os.path.join(BASE_DIR, 'model_lstm.keras')
    return load_model(model_path)

@st.cache_resource
def load_scaler():
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    return joblib.load(scaler_path)

@st.cache_data
def load_historical_data():
    data_path = os.path.join(BASE_DIR, 'Juli 2024 - Juli 2026.xlsx')
    df = pd.read_excel(data_path)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    return df

# Memanggil fungsi load secara aman
try:
    model_lstm = load_my_lstm_model()
    scaler = load_scaler()
    df_filtered = load_historical_data()
    model_loaded = True
except Exception as e:
    st.error(f"Gagal memuat model, scaler, atau data: {e}")
    st.info("Pastikan 'model_lstm.keras', 'scaler.pkl', dan file Excel sudah berada di direktori yang sama dengan 'app.py'.")
    model_loaded = False

# Nilai evaluasi statis dari hasil training sebelumnya
metrics_data = {
    'MAE': 6.627,
    'RMSE': 12.857,
    'MAPE': 162.595
}

# Jika semua berhasil dimuat
if model_loaded:
    # ==============================================================================
    # 3. SIDEBAR / PANEL KONTROL
    # ==============================================================================
    st.sidebar.header("🎛️ Panel Kontrol")
    
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
    * **Format File:** Native Keras (.keras) & Scaler (.pkl)
    """)
    
    # ==============================================================================
    # 4. GRID METRIK EVALUASI MODEL
    # ==============================================================================
    st.subheader("📊 Metrik Evaluasi Model (Data Uji)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="MAE (Mean Absolute Error)", value=f"{metrics_data['MAE']} mm")
    with col2:
        st.metric(label="RMSE (Root Mean Squared Error)", value=f"{metrics_data['RMSE']} mm")
    with col3:
        st.metric(label="MAPE", value=f"{metrics_data['MAPE']:.3f} %")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==============================================================================
    # 5. PROSES FORECASTING REKURSIF DENGAN SCALER (13 FITUR)
    # ==============================================================================
    # Bersihkan nama kolom dari spasi tidak terlihat (misal 'TN ' menjadi 'TN')
    df_filtered.columns = df_filtered.columns.str.strip()

    # Daftar 13 kolom fitur yang seharusnya dicari
    fitur_target = ['TN', 'TX', 'TAVG', 'RH_AVG', 'SS', 'FF_X', 'DDD_X', 'FF_AVG', 
                   'RR_lag_1', 'RR_lag_3', 'RR_lag_7', 'bulan', 'hari']
    
    # FILTER: Ambil hanya kolom yang BENAR-BENAR ada di dalam file Excel Anda
    fitur_kolom = [col for col in fitur_target if col in df_filtered.columns]

    # Cek jika ada kolom yang kurang/hilang dari Excel Anda
    kolom_hilang = set(fitur_target) - set(fitur_kolom)
    if kolom_hilang:
        st.warning(f"⚠️ Perhatian: Kolom berikut tidak ditemukan di file Excel Anda: {list(kolom_hilang)}. Aplikasi akan mencoba berjalan dengan {len(fitur_kolom)} kolom yang tersedia.")

    if len(fitur_kolom) == 0:
        st.error("Error Fatal: Tidak ada satupun kolom fitur yang cocok ditemukan di dalam file Excel Anda!")
    else:
        # Ambil baris terakhir data mentah/asli sesuai dengan fitur yang ditemukan
        last_features_raw = df_filtered[fitur_kolom].iloc[-1].values.astype(np.float32).reshape(1, -1)
        
        # JIKA jumlah kolom pas 13, jalankan forecasting seperti biasa
        if len(fitur_kolom) == 13:
            future_predictions = []
            
            for i in range(horizon):
                # 1. Lakukan scaling pada fitur mentah
                last_input_scaled = scaler.transform(last_features_raw).flatten()
                current_input_3d = np.reshape(last_input_scaled, (1, 1, len(last_input_scaled)))
                
                # 2. Prediksi (menghasilkan nilai mm asli)
                pred_val = model_lstm.predict(current_input_3d, verbose=0).flatten()[0]
                pred_val = max(0.0, float(pred_val))
                future_predictions.append(pred_val)
                
                # 3. Geser window pada data mentah secara autoregressive
                new_features_raw = np.roll(last_features_raw, -1)
                new_features_raw[0, -1] = pred_val 
                
                last_features_raw = new_features_raw
                
            # Index tanggal masa depan
            last_date = pd.to_datetime(df_filtered['Tanggal'].iloc[-1])
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
            df_forecast = pd.DataFrame({'Tanggal': future_dates, 'Prediksi Curah Hujan (mm)': future_predictions})
            
            # (Lanjutkan ke Bagian 6 & 7 di bawah untuk visualisasi grafik dan tabel menggunakan df_forecast)
        else:
            st.error(f"Scaler Anda membutuhkan tepat 13 fitur, tetapi di file Excel hanya ditemukan {len(fitur_kolom)} fitur. Harap sesuaikan nama kolom di file Excel Anda agar tepat mengandung kolom: {fitur_target}")    
    # ==============================================================================
    # 6. VISUALISASI GRAFIK
    # ==============================================================================
    st.subheader("📈 Visualisasi Data Aktual dan Hasil Forecast")
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Plot Data Historis Aktual (30 Hari Terakhir)
    dates_actual = df_filtered['Tanggal'].iloc[-30:]
    y_actual = df_filtered['RR'].iloc[-30:]
    ax.plot(dates_actual, y_actual, label='Data Aktual (30 Hari Terakhir)', color='black', linewidth=2, marker='o', markersize=3)
    
    # Plot Data Hasil Forecast
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
