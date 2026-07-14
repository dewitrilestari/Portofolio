import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

# ====================================================================
# 1. MONKEY PATCHING UNTUK LAYER DENSE KERAS (Mencegah error kuantisasi)
# ====================================================================
import tensorflow as tf
from tensorflow.keras.layers import Dense

original_dense_from_config = Dense.from_config

def patched_dense_from_config(cls, config):
    config.pop('quantization_config', None)
    return original_dense_from_config(config)

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
    
    # 1. Pastikan kolom Tanggal bertipe Datetime
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    
    # 2. Bersihkan nama kolom dari spasi tidak terlihat
    df.columns = df.columns.str.strip()
    
    # 3. Pastikan nilai Curah Hujan (RR) tidak negatif
    if 'RR' in df.columns:
        df['RR'] = df['RR'].clip(lower=0.0)
    
    # --- REKAYASA FITUR OTOMATIS (MENGATASI KOLOM YANG HILANG DI EXCEL) ---
    # A. Ekstrak fitur kalender
    if 'bulan' not in df.columns:
        df['bulan'] = df['Tanggal'].dt.month
    if 'hari' not in df.columns:
        df['hari'] = df['Tanggal'].dt.day
        
    # B. Membuat fitur Lag otomatis dari kolom target 'RR'
    if 'RR' in df.columns:
        if 'RR_lag_1' not in df.columns:
            df['RR_lag_1'] = df['RR'].shift(1)
        if 'RR_lag_3' not in df.columns:
            df['RR_lag_3'] = df['RR'].shift(3)
        if 'RR_lag_7' not in df.columns:
            df['RR_lag_7'] = df['RR'].shift(7)
            
    # C. Hapus baris kosong (NaN) akibat proses pergeseran lag (.shift)
    df = df.dropna().reset_index(drop=True)
    
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

# Nilai evaluasi statis dari hasil training Google Colab
metrics_data = {
    'MAE': 6.627,
    'RMSE': 12.857,
    'MAPE': 162.595
}

# Jika semua komponen berhasil dimuat
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
    # 5. PROSES FORECASTING REKURSIF DENGAN SCALER (13 FITUR) - FIXED LOGIC
    # ==============================================================================
    # Daftar 13 kolom fitur wajib yang dibutuhkan oleh StandardScaler
    fitur_kolom = ['TN', 'TX', 'TAVG', 'RH_AVG', 'SS', 'FF_X', 'DDD_X', 'FF_AVG', 
                   'RR_lag_1', 'RR_lag_3', 'RR_lag_7', 'bulan', 'hari']
    
    # Validasi apakah ke-13 kolom kini sudah lengkap di dataframe setelah rekayasa fitur
    fitur_tersedia = [col for col in fitur_kolom if col in df_filtered.columns]
    
    if len(fitur_tersedia) == 13:
        # Ambil baris terakhir data mentah sebagai DataFrame agar nama kolomnya terjaga
        last_row = df_filtered[fitur_kolom].iloc[-1:].copy()
        
        future_predictions = []
        current_row = last_row.copy()
        
        # Dapatkan tanggal awal mulai prediksi (1 hari setelah tanggal terakhir di dataset)
        last_date = pd.to_datetime(df_filtered['Tanggal'].iloc[-1])
        current_date = last_date
        
        # Ambil riwayat curah hujan aktual terakhir untuk mengisi lag secara presisi
        prediction_history = list(df_filtered['RR'].iloc[-10:].values) 
        
        for i in range(horizon):
            # Maju 1 hari
            current_date = current_date + pd.Timedelta(days=1)
            
            # A. Susun fitur-fitur lag secara presisi berdasarkan riwayat di buffer
            current_row['RR_lag_1'] = prediction_history[-1]  # H-1
            current_row['RR_lag_3'] = prediction_history[-3]  # H-3
            current_row['RR_lag_7'] = prediction_history[-7]  # H-7
            
            # B. Update fitur penanda waktu sesuai tanggal simulasi berjalan
            current_row['bulan'] = current_date.month
            current_row['hari'] = current_date.day
            
            # C. Ambil array fitur sesuai urutan wajib StandardScaler (Kirimkan sebagai DataFrame)
            features_to_scale = current_row[fitur_kolom]
            
            # D. Scaling & Reshape ke format 3D untuk LSTM
            features_scaled = scaler.transform(features_to_scale)
            features_3d = np.reshape(features_scaled, (1, 1, features_scaled.shape[1]))
            
            # E. Prediksi
            pred_val = model_lstm.predict(features_3d, verbose=0).flatten()[0]
            pred_val = max(0.0, float(pred_val))  # Amankan dari nilai negatif
            
            # Simpan hasil prediksi
            future_predictions.append(pred_val)
            prediction_history.append(pred_val) # Masukkan ke buffer untuk lag berikutnya
            
        # Membuat indeks tanggal masa depan berdasarkan tanggal terakhir di dataset
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
        df_forecast = pd.DataFrame({'Tanggal': future_dates, 'Prediksi Curah Hujan (mm)': future_predictions})
        
        # ==============================================================================
        # 6. VISUALISASI GRAFIK (FIXED SCALE & NO LATEX ERROR)
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
            
    else:
        # Jika rekayasa fitur gagal melengkapi ke-13 kolom
        st.error(f"Gagal melakukan rekayasa fitur otomatis. Scaler membutuhkan tepat 13 fitur, tetapi sistem hanya berhasil mendeteksi/membuat {len(fitur_tersedia)} fitur.")
        st.info(f"Kolom yang terdeteksi saat ini: {fitur_tersedia}")
