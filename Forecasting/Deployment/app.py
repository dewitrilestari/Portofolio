import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

# Set Page Config di awal untuk mematikan potensi konflik layout
st.set_page_config(page_title="Forecasting Curah Hujan BMKG", layout="wide")

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
    
    # Pastikan kolom Tanggal bertipe Datetime
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    
    # Bersihkan nama kolom dari spasi tidak terlihat
    df.columns = df.columns.str.strip()
    
    # Pastikan nilai Curah Hujan (RR) tidak ada yang bernilai negatif
    if 'RR' in df.columns:
        df['RR'] = df['RR'].clip(lower=0.0)
    
    # --- REKAYASA FITUR OTOMATIS (MENGATASI KOLOM YANG HILANG DI EXCEL) ---
    if 'bulan' not in df.columns:
        df['bulan'] = df['Tanggal'].dt.month
    if 'hari' not in df.columns:
        df['hari'] = df['Tanggal'].dt.day
        
    if 'RR' in df.columns:
        if 'RR_lag_1' not in df.columns:
            df['RR_lag_1'] = df['RR'].shift(1)
        if 'RR_lag_3' not in df.columns:
            df['RR_lag_3'] = df['RR'].shift(3)
        if 'RR_lag_7' not in df.columns:
            df['RR_lag_7'] = df['RR'].shift(7)
            
    # Hapus baris kosong akibat pergeseran lag
    df = df.dropna().reset_index(drop=True)
    return df

# Memanggil fungsi load secara aman
try:
    model_lstm = load_my_lstm_model()
    scaler = load_scaler()
    df_filtered = load_historical_data()
    model_loaded = True
except Exception as e:
    st.error(f"Gagal memuat komponen: {e}")
    model_loaded = False

# Nilai evaluasi statis dari hasil training
metrics_data = {
    'MAE': 6.627,
    'RMSE': 12.857
}

# Jika semua komponen berhasil dimuat
if model_loaded:
    # ==============================================================================
    # REVISI 1: PENAMBAHAN INFORMASI APLIKASI DI SIDEBAR (PRIORITAS TINGGI)
    # ==============================================================================
    with st.sidebar:
        st.header("ℹ️ Tentang Aplikasi")
        st.info("""
        **Tujuan Aplikasi:**
        Dashboard ini dirancang untuk memprediksi (*forecasting*) akumulasi curah hujan harian (RR) secara otomatis sebagai sistem pendukung keputusan mitigasi bencana hidrometeorologi.
        """)
        
        st.header("⚙️ Detail Teknis")
        st.markdown(f"""
        * **Sumber Data:** Dataset Cuaca BMKG Sleman, DIY (Juli 2024 - Juli 2026)
        * **Ukuran Data:** ~730 data rekaman harian
        * **Model Prediksi:** Long Short-Term Memory (LSTM) Deep Learning
        * **Ekstraksi Fitur:** Parameter Makro Cuaca + Fitur Autoregresif Lag (H-1, H-3, H-7)
        """)
        
        st.markdown("---")
        
        st.header("🎛️ Panel Kontrol")
        # Meletakkan selectbox di dalam scope container sidebar yang bersih
        horizon = st.selectbox(
            "Pilih Horizon Forecasting (Hari):",
            options=[7, 14, 30],
            index=0,
            key="horizon_selector"
        )
        st.markdown("<br>" * 10, unsafe_allow_html=True)
    
    # ==============================================================================
    # Halaman Utama Dashboard
    # ==============================================================================
    st.title("🌧️ Dashboard Forecasting Curah Hujan BMKG (LSTM)")
    st.markdown("Aplikasi berbasis kecerdasan buatan untuk meramal intensitas curah hujan berdasarkan pola runtun waktu (*time-series*).")
    
    # ==============================================================================
    # GRID METRIK EVALUASI MODEL
    # ==============================================================================
    st.subheader("📊 Metrik Evaluasi Model (Data Uji)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="MAE (Mean Absolute Error)", value=f"{metrics_data['MAE']} mm")
    with col2:
        st.metric(label="RMSE (Root Mean Squared Error)", value=f"{metrics_data['RMSE']} mm")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==============================================================================
    # PROSES FORECASTING REKURSIF (FIXED LOGIC)
    # ==============================================================================
    fitur_kolom = ['TN', 'TX', 'TAVG', 'RH_AVG', 'SS', 'FF_X', 'DDD_X', 'FF_AVG', 
                   'RR_lag_1', 'RR_lag_3', 'RR_lag_7', 'bulan', 'hari']
    
    fitur_tersedia = [col for col in fitur_kolom if col in df_filtered.columns]
    
    if len(fitur_tersedia) == 13:
        last_row = df_filtered[fitur_kolom].iloc[-1:].copy()
        
        future_predictions = []
        current_row = last_row.copy()
        
        last_date = pd.to_datetime(df_filtered['Tanggal'].iloc[-1])
        current_date = last_date
        
        prediction_history = list(df_filtered['RR'].iloc[-10:].values) 
        
        for i in range(horizon):
            current_date = current_date + pd.Timedelta(days=1)
            
            # Susun fitur-fitur lag secara presisi berdasarkan riwayat aktual/prediksi
            current_row['RR_lag_1'] = prediction_history[-1]  
            current_row['RR_lag_3'] = prediction_history[-3]  
            current_row['RR_lag_7'] = prediction_history[-7]  
            
            # Update fitur kalender
            current_row['bulan'] = current_date.month
            current_row['hari'] = current_date.day
            
            # Scaling & Reshape ke format 3D untuk LSTM
            features_to_scale = current_row[fitur_kolom]
            features_scaled = scaler.transform(features_to_scale)
            features_3d = np.reshape(features_scaled, (1, 1, features_scaled.shape[1]))
            
            # Prediksi nilai curah hujan asli
            pred_val = model_lstm.predict(features_3d, verbose=0).flatten()[0]
            pred_val = max(0.0, float(pred_val))  
            
            future_predictions.append(pred_val)
            prediction_history.append(pred_val) 
            
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq='D')
        df_forecast = pd.DataFrame({'Tanggal': future_dates, 'Prediksi Curah Hujan (mm)': future_predictions})
        
        # ==============================================================================
        # VISUALISASI GRAFIK
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
        # MENAMPILKAN NILAI PREDIKSI DALAM TABEL
        # ==============================================================================
        st.subheader(f"📋 Tabel Nilai Hasil Prediksi ({horizon} Hari ke Depan)")
        
        df_table = df_forecast.copy()
        df_table['Tanggal'] = df_table['Tanggal'].dt.strftime('%Y-%m-%d')
        df_table['Prediksi Curah Hujan (mm)'] = df_table['Prediksi Curah Hujan (mm)'].round(3)
        
        col_table, col_empty = st.columns([0.6, 0.4])
        with col_table:
            st.dataframe(df_table, use_container_width=True, hide_index=True)
            
    else:
        st.error(f"Gagal memproses data. Scaler membutuhkan 13 fitur, hanya tersedia {len(fitur_tersedia)}.")

    # ==============================================================================
    # REVISI 2: PROFESIONALISME & KONTAK (FOOTER APLIKASI AMAN YANG DIBATASI ST.CONTAINER)
    # ==============================================================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    footer_container = st.container()
    with footer_container:
        st.markdown(
            """
            <div style="text-align: center; color: #666666; font-size: 14px; padding-bottom: 20px;">
                <p style="margin-bottom: 5px;"><strong>Created by Dewi Tri Lestari</strong></p>
                <p style="margin-top: 0px;">
                    <a href="https://github.com/dewitrilestari/Portofolio/Forecasting" target="_blank" style="color: #1f77b4; text-decoration: none; margin-right: 20px; font-weight: bold;">🐙 GitHub Portfolio</a>
                    <a href="https://linkedin.com/in/dewitrilestari" target="_blank" style="color: #1f77b4; text-decoration: none; font-weight: bold;">👔 LinkedIn Profile</a>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
