# 🪪 Sistem OCR KTP & Validasi AI (e-KTP)

Aplikasi web berbasis kecerdasan buatan (*Vision AI & OCR*) untuk mengklasifikasi dokumen KTP Indonesia, mengekstrak data identitas secara terstruktur (JSON), serta menjalankan validasi *business rules* NIK secara otomatis, dibangun menggunakan **Streamlit** dan **OpenRouter API**.

* **Live Demo:** https://ai-ktp-test.streamlit.app/
* **Model AI:** OpenAI GPT-4o (Vision OCR) & Google Gemini / GPT-4o-Mini (Classification)
* **API Gateway:** OpenRouter API
* **Penyimpanan Data:** SQLite Database (`ktp_database.db`)

---

## 📌 Tentang Project

Proyek ini berfokus pada otomasi proses **e-KYC (Electronic Know Your Customer)** untuk ekstraksi dan validasi dokumen KTP Indonesia. Menggunakan arsitektur *Multimodal Vision AI*, sistem ini mampu mengenali apakah dokumen yang diunggah berupa KTP resmi, membaca 14 bidang data teks dengan presisi tinggi, dan mencocokkan logika nomor NIK secara deterministik.

Tantangan utama dalam pemrosesan data identitas publik adalah risiko kebocoran data sensitif (*Personally Identifiable Information / PII*) dan keamanan kredensial. Aplikasi ini menerapkan sistem **Data Masking otomatis** pada tampilan antarmuka (UI) serta manajemen **Streamlit Secrets & `.env`** agar API Key dan data pribadi pengguna tetap terlindungi sepenuhnya di repositori publik.

---

## 🎯 Tujuan Sistem

* **Otomasi Klasifikasi & OCR:** Memverifikasi keabsahan jenis dokumen dan mengekstrak data teks KTP secara otomatis tanpa masukan manual.
* **Validasi Aturan Bisnis NIK:** Memeriksa kesesuaian 16 digit NIK terhadap format angka, jenis kelamin, serta tanggal lahir pemilik KTP secara akurat.
* **Perlindungan Data Pribadi (PDP):** Menyediakan mekanisme *masking* otomatis pada data sensitif (NIK, Nama, TTL, Alamat) sebelum ditampilkan ke antarmuka pengguna.
* **Integrasi Database Terstruktur:** Menyimpan riwayat hasil ekstraksi dan status validasi ke dalam database SQLite lokal untuk kebutuhan *audit trail*.

---

## 🗂️ Struktur Project

```text
AI_KTP/
├── Deployment/
│   ├── app.py                  # Aplikasi Utama Streamlit
│   ├── ktp_database.db         # Database SQLite Penyimpanan History
│   ├── .env.example            # Contoh Konfigurasi Environment Variable
│   └── requirements.txt        # Library Dependencies (Streamlit, Requests, Pillow, dll)
├── Notebook/
│   └── notebook.ipynb          # Notebook Eksperimen AI Vision & Preprocessing
└── README.md                   # Dokumentasi Proyek

