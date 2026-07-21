import os
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import tensorflow as tf

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Forecasting Curah Hujan BMKG", page_icon="🌧️", layout="wide"
)

st.title("🌧️ Aplikasi Forecasting Curah Hujan (RR) BMKG - LSTM")
st.markdown(
    "Aplikasi web ini menggunakan model **Deep Learning LSTM** untuk memprediksi akumulasi curah hujan harian secara otomatis."
)

# ==========================================
# 2. LOAD MODEL & SCALER (CACHE RESOURCE)
# ==========================================
@st.cache_resource
def load_artifacts():
    # Mengambil lokasi direktori tempat app.py berada secara presisi
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    scaler_path = os.path.join(BASE_DIR, "scaler.pkl")
    model_keras_path = os.path.join(BASE_DIR, "model_lstm.keras")
    model_h5_path = os.path.join(BASE_DIR, "model_lstm.h5")

    # Deteksi file model
    if os.path.exists(model_keras_path):
        model_path = model_keras_path
    elif os.path.exists(model_h5_path):
        model_path = model_h5_path
    else:
        st.error(
            f"❌ Model LSTM (model_lstm.keras / model_lstm.h5) tidak ditemukan di folder: `{BASE_DIR}`"
        )
        st.stop()

    if not os.path.exists(scaler_path):
        st.error(
            f"❌ File scaler.pkl tidak ditemukan di folder: `{BASE_DIR}`"
        )
        st.stop()

    model = tf.keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler

model_lstm, scaler = load_artifacts()
# ==========================================
# 3. SIDEBAR & PEMUATAN DATASET
# ==========================================
st.sidebar.header("⚙️ Pengaturan Data & Parameter")

data_url = "https://raw.github.com/dewitrilestari/Portofolio/main/Forecasting/Merge%20Data/Juli%202024%20-%20Juli%202026.xlsx"

uploaded_file = st.sidebar.file_uploader(
    "Upload File Dataset (Excel/CSV)", type=["xlsx", "csv"]
)


@st.cache_data
def load_data(file_source):
    if isinstance(file_source, str):
        df = pd.read_excel(file_source)
    else:
        if file_source.name.endswith(".csv"):
            df = pd.read_csv(file_source)
        else:
            df = pd.read_excel(file_source)
    return df


try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.sidebar.success("✅ File kustom berhasil diunggah!")
    else:
        df = load_data(data_url)
        st.sidebar.info("ℹ️ Menggunakan dataset default (GitHub).")
except Exception as e:
    st.error(f"Gagal memuat dataset: {e}")
    st.stop()

# Preprocessing Ringan Data Awal
df["Tanggal"] = pd.to_datetime(df["Tanggal"])
if "RR" in df.columns:
    df["RR"] = df["RR"].clip(lower=0)

# Tampilkan ringkasan data
st.subheader("📊 Data Historis Terakhir")
st.dataframe(df.tail(10), use_container_width=True)

# ==========================================
# 4. PROSES FORECASTING FUTURE
# ==========================================
forecast_days_option = st.sidebar.slider(
    "Pilih Rentang Forecast (Hari ke Depan):",
    min_value=7,
    max_value=30,
    value=14,
    step=1,
)

if st.sidebar.button("🚀 Jalankan Prediksi Future Forecast"):
    with st.spinner("Sedang memproses prediksi LSTM..."):
        forecast_periods = [7, 14, 30]
        max_forecast = max(forecast_periods)

        # 1. Ambil daftar fitur resmi yang dipelajari scaler saat training
        expected_features = list(scaler.feature_names_in_)

        # 2. Siapkan data X (Fitur Prediktor)
        X_data = df.drop(columns=["Tanggal", "DDD_CAR", "RR"], errors="ignore")

        # Ambil nilai baris terakhir sebagai baseline eksogen
        baseline_row = X_data.iloc[-1]

        future_predictions = []
        last_date = df["Tanggal"].iloc[-1]
        current_date = last_date

        # Loop prediksi harian
        for i in range(max_forecast):
            current_date = current_date + pd.Timedelta(days=1)

            # Buat baris baru menggunakan nilai baseline
            current_row = pd.Series(index=X_data.columns, dtype="float64")
            for col in X_data.columns:
                current_row[col] = baseline_row[col]

            # 3. Penanganan Dimensi & Konversi ke DataFrame 2D (Mencegah ValueError)
            if isinstance(current_row, pd.Series):
                features_to_scale = pd.DataFrame([current_row])
            else:
                row_2d = np.array(current_row).reshape(1, -1)
                features_to_scale = pd.DataFrame(row_2d)

            # 4. Filter HANYA kolom yang dikenal oleh scaler (Mencegah Error Unseen Feature)
            features_to_scale_filtered = features_to_scale[expected_features]

            # 5. Scaling & Reshape 3D Khusus LSTM (1, 1, num_features)
            features_scaled = scaler.transform(features_to_scale_filtered)
            features_3d = np.reshape(
                features_scaled, (1, 1, features_scaled.shape[1])
            )

            # 6. Prediksi LSTM & Reverse Transform dari Log ke mm
            pred_val_log = model_lstm.predict(features_3d, verbose=0).flatten()[
                0
            ]
            pred_val = np.expm1(pred_val_log)
            pred_val = max(0.0, float(pred_val))

            future_predictions.append(pred_val)

        # Generate Tanggal Masa Depan
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=max_forecast,
            freq="D",
        )

        # ==========================================
        # 5. VISUALISASI HASIL & DOWNLOAD
        # ==========================================
        st.subheader("📈 Visualisasi Hasil Forecasting Curah Hujan")

        fig, ax = plt.subplots(figsize=(12, 5))

        # Plot 30 Hari Aktual Terakhir
        dates_actual_plot = df["Tanggal"].iloc[-30:]
        y_actual_plot = df["RR"].iloc[-30:]
        ax.plot(
            dates_actual_plot,
            y_actual_plot,
            label="Data Aktual (30 Hari Terakhir)",
            color="black",
            linewidth=2,
        )

        # Plot Garis Forecast 7, 14, dan 30 Hari
        colors = {7: "green", 14: "blue", 30: "red"}
        styles = {7: "-", 14: "--", 30: "-."}

        for days in forecast_periods:
            ax.plot(
                future_dates[:days],
                future_predictions[:days],
                label=f"Forecast {days} Hari ke Depan",
                color=colors.get(days, "purple"),
                linestyle=styles.get(days, "-"),
                marker="o",
                markersize=4,
            )

        ax.set_title("Visualisasi Future Forecasting Curah Hujan (RR) - Model LSTM")
        ax.set_xlabel("Tanggal")
        ax.set_ylabel("Curah Hujan (mm)")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        fig.autofmt_xdate()

        st.pyplot(fig)

        # Tabel Output Sesuai Pilihan Slider
        df_forecast_res = pd.DataFrame(
            {
                "Tanggal": future_dates[:forecast_days_option],
                "Prediksi Curah Hujan (mm)": [
                    round(p, 2)
                    for p in future_predictions[:forecast_days_option]
                ],
            }
        )

        st.subheader(
            f"📋 Tabel Hasil Forecasting ({forecast_days_option} Hari ke Depan)"
        )
        st.dataframe(df_forecast_res, use_container_width=True)

        # Fitur Unduh Hasil Prediksi (CSV)
        csv_data = df_forecast_res.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Hasil Prediksi (CSV)",
            data=csv_data,
            file_name=f"forecast_curah_hujan_{forecast_days_option}hari.csv",
            mime="text/csv",
        )
