# 🌧️ Aplikasi Forecasting Curah Hujan BMKG (LSTM)

Aplikasi web berbasis kecerdasan buatan (*Deep Learning*) untuk memprediksi akumulasi curah hujan harian (RR) masa depan menggunakan model **Long Short-Term Memory (LSTM)** dan metode peramalan rekursif multi-step (*multi-step recursive forecasting*), dibangun dengan **Streamlit**.

* **Live Demo:** https://github.com/dewitrilestari/Portofolio/edit/main/Forecasting/
* **Sumber Data:** https://dataonline.bmkg.go.id/

---

## 📌 Tentang Project

Project ini berfokus pada pemodelan runtun waktu (*time-series forecasting*) untuk memprediksi intensitas curah hujan harian berdasarkan data historis stasiun meteorologi BMKG. Menggunakan arsitektur jaringan saraf berulang LSTM (*Recurrent Neural Network*), model ini mampu mempelajari ketergantungan sekuensial jangka panjang dari 13 parameter makro cuaca dan fitur lag waktu.

Tantangan utama dalam peramalan rekursif multi-langkah (7, 14, hingga 30 hari ke depan) adalah akumulasi kesalahan dan risiko ledakan numerik (*exponential explosion*). Aplikasi ini menerapkan manajemen *sliding window buffer* yang presisi dan integrasi *StandardScaler* dinamis agar setiap langkah proyeksi autoregresif tetap berjalan stabil di skala angka riil yang realistis (milimeter).

---

## 🎯 Tujuan Analisis

* Memprediksi akumulasi curah hujan harian secara akurat untuk horizon waktu 7, 14, hingga 30 hari ke depan.
* Mendukung sistem peringatan dini (*early warning system*) untuk mitigasi bencana hidrometeorologi seperti banjir, tanah longsor, dan kekeringan.
* Mengotomatisasi rekayasa fitur temporal dan lag spasial data cuaca secara *real-time* saat inferensi bergulir.
* Menyajikan visualisasi data historis versus hasil proyeksi masa depan dalam grafik interaktif yang mudah dipahami oleh *stakeholder*.

---

## 🗂️ Struktur Project

```text
Forecasting-Curah-Hujan/
├── app.py                      # Aplikasi Utama Streamlit
├── model_lstm.keras            # Model LSTM Terlatih (Format Native Keras)
├── scaler.pkl                  # StandardScaler Objek (Scikit-Learn)
├── Juli 2024 - Juli 2026.xlsx  # Dataset Historis Parameter Cuaca BMKG
├── requirements.txt            # Library Dependencies (TensorFlow, Streamlit, dll)
└── README.md                   # Dokumentasi Proyek
```

**## ⚙️ Fitur Dashboard**

| Nama Fitur | Tampilan / Representasi Visual | Keterangan & Detail Teknis |
| :--- | :--- | :--- |
| **Recursive Multi-Step Forecast** | Pilihan Dropdown (*7, 14, 30 Hari*) | Melakukan proyeksi curah hujan secara runtun (*autoregressive*) berdasarkan durasi hari yang dipilih pengguna secara dinamis. |
| **Model Evaluation Metrics** | Grid Card Informasi Teratas | Menampilkan metrik performa model hasil pengujian data uji secara transparan: **MAE (6.627 mm)**, **RMSE (12.857 mm)**, dan **MAPE (162.595%)**. |
| **Automatic Feature Engineering** | Integrasi Sistem Latar Belakang | Secara otomatis mengekstrak penanda waktu (`bulan`, `hari`) dan melacak riwayat nilai lag (`RR_lag_1`, `RR_lag_3`, `RR_lag_7`) dari data masukan terakhir. |
| **Synchronized Scaling Pipeline** | Transformasi Data Otomatis | Memastikan data mentah diselaraskan menggunakan `StandardScaler` sebelum dibentuk ke dalam tensor 3D untuk inferensi aman pada model LSTM. |
| **Interactive Temporal Visualization** | Grafik Line-Chart Multi-Warna | Menyajikan visualisasi kontras antara **30 Hari Data Aktual Terakhir** (berwarna hitam) yang bersambung langsung dengan **Garis Prediksi** (merah putus-putus). |
| **Tabular Forecast Export** | Tabel Data Interaktif | Menampilkan ringkasan hasil angka prediksi numerik yang presisi (dibulatkan hingga 3 desimal) lengkap dengan kolom tanggal proyeksi. |
| **Professional Branding Footer** | Bagian Terbawah Aplikasi | Menyediakan tautan portofolio profesional berupa ikon tautan langsung menuju profil **GitHub** dan **LinkedIn** pembuat aplikasi. |

**## 📊 Metode yang Digunakan**

### 1. Real-time Feature Engineering & Autoregressive Buffer
Untuk melakukan prediksi bergulir (*multi-step ahead forecasting*), model membutuhkan nilai historis runtun waktu berupa fitur lag ($t-1$, $t-3$, $t-7$) dari target variabel Curah Hujan (`RR`). Di dalam sistem inferensi Streamlit, dibuat mekanisme *buffer* dinamis yang berjalan secara otomatis:
* **Pergeseran Lag Dinamis:** Nilai hasil prediksi pada hari ke-$t$ langsung digeser masuk ke dalam *buffer* antrean untuk menjadi fitur `RR_lag_1` pada iterasi prediksi hari ke-$t+1$.
* **Sinkronisasi Kalender:** Fitur penanda waktu (`bulan` dan `hari`) diperbarui secara dinamis menyesuaikan penanggalan riil sepanjang simulasi peramalan bergulir agar model peka terhadap pola musiman cuaca.

### 2. Sequence Modeling via LSTM (Long Short-Term Memory)
Arsitektur LSTM (*Recurrent Neural Network*) digunakan karena kemampuannya yang unggul dalam mengingat ketergantungan sekuensial jangka panjang (*long-term dependencies*) pada data iklim.
* **Format Input 3D:** Data masukan ditransformasi ke dalam dimensi tensor 3D dengan bentuk `(batch_size, timesteps, features)` sebelum diumpankan ke model.
* **Pipeline Scaling Sinkron:** Guna mencegah terjadinya penyimpangan gradien atau ledakan numerik (*exponential explosion*) selama perulangan, nilai prediksi baru distandardisasi ulang menggunakan objek `StandardScaler` terlatih sebelum lanjut ke langkah peramalan berikutnya.
```python
# Potongan logika transformasi aman pada loop rekursif app.py:
features_to_scale = current_row[fitur_kolom]
features_scaled = scaler.transform(features_to_scale)
features_3d = np.reshape(features_scaled, (1, 1, features_scaled.shape[1]))
pred_val = model_lstm.predict(features_3d)
```

**## 🚀 Cara Menjalankan Lokal**
```python
# Clone repository
git clone [https://github.com/](https://github.com/)[UsernameKamu]/[NamaRepo].git

# Masuk ke folder project
cd Forecasting-Curah-Hujan

# Install dependency yang dibutuhkan
pip install -r requirements.txt

# Jalankan aplikasi Streamlit
streamlit run app.py
```

**🌐 Deploy**
Aplikasi ini dideploy menggunakan Streamlit Community Cloud yang terhubung langsung dengan repositori GitHub Anda. Setiap kali ada pembaruan file model (model_lstm.keras), scaler baru, ataupun pembaruan kode visualisasi di GitHub, server akan memperbarui visualisasi dashboard secara otomatis (Continuous Deployment).

**🛠️ Tech Stack**
* Python (Bahasa Pemrograman Utama)
* Streamlit (Framework Aplikasi Web/Dashboard)
* TensorFlow / Keras (Arsitektur Deep Learning LSTM)
* Scikit-Learn (Preprocessing Data & StandardScaler)
* Pandas & NumPy (Manipulasi Data Runtun Waktu)
* Matplotlib (Visualisasi Grafik Tren Curah Hujan)

**📈 Manfaat Praktis & Bisnis**
* Sektor Pertanian: Membantu petani menentukan jadwal tanam dan panen berdasarkan proyeksi curah hujan jangka pendek hingga menengah.
* Manajemen Sumber Daya Air (Waduk/Bendungan): Memberikan estimasi limpasan air hujan untuk mencegah kegagalan struktur bendungan.
* Sektor Logistik & Transportasi: Memitigasi risiko hambatan rute pengiriman akibat cuaca buruk ekstrem.
* Portofolio Terapan: Menjadi bukti kompetensi penanganan data deret waktu menggunakan Deep Learning dan deployment end-to-end yang solid.

⚠️ Catatan Penting
* Batasan Model (Error Accumulation): Karena menggunakan metode peramalan rekursif (autoregressive feedback loop), hasil prediksi untuk jangka waktu yang sangat panjang (seperti mendekati hari ke-30) secara alami akan cenderung melandai menuju nilai rata-rata musiman (converge to mean).
* Ketergantungan Data Cuaca: Keakuratan prediksi masa depan sangat mengandalkan konsistensi input parameter cuaca makro lainnya (seperti suhu dan kelembapan) yang diasumsikan stabil mengikuti tren hari terakhir.
