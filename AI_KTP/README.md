# 🪪 Sistem OCR KTP & Validasi AI (e-KYC)

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
```
---

## ⚙️ Fitur Dashboard

| Nama Fitur | Tampilan / Representasi Visual | Keterangan & Detail Teknis |
| :--- | :--- | :--- |
| **Document Classification** | Status Badge (*KTP / Bukan KTP*) | Mengidentifikasi apakah gambar yang diunggah adalah KTP Indonesia menggunakan model Multimodal Vision (`openai/gpt-4o-mini` / `google/gemini-2.0-flash`). |
| **High-Precision Vision OCR** | Tabel Data Format JSON | Mengekstrak 14 bidang teks KTP (NIK, Nama, TTL, Alamat, RT/RW, Agama, dll.) secara terstruktur dengan tingkat akurasi tinggi menggunakan `openai/gpt-4o`. |
| **Deterministic Business Rule Validation** | Tabel Status Per Aturan (*VALID / INVALID*) | Menguji keabsahan NIK: pengecekan 16 digit angka, pemutakhiran tanggal lahir, serta validasi pola jenis kelamin (pria vs wanita di mana tanggal +40). |
| **Automated Data Masking (Privacy Protection)** | Teks Disamarkan (*Contoh: 3471XXXXXXXXXXXX*) | Menyamarkan data sensitif pengguna secara otomatis sebelum dirender ke layar untuk menjaga privasi di repositori publik. |
| **SQLite History Logging** | Halaman *Database History* | Menyimpan data hasil ekstraksi ke database SQLite (`ktp_database.db`) dan menampilkan tabel riwayat transaksi secara terorganisir. |
| **Secure Credentials Management** | Konfigurasi Secrets / `.env` | Mengamankan API Key menggunakan Streamlit Secrets (`st.secrets`) dan file `.env` yang dilindungi oleh `.gitignore`. |
| **Professional Branding Footer** | Bagian Terbawah Aplikasi | Menyediakan tautan portofolio berupa ikon tautan langsung menuju profil **GitHub** dan **LinkedIn** pembuat aplikasi. |

---

## 📊 Metode yang Digunakan

### 1. Preprocessing Gambar & Base64 Encoding
Sebelum dikirim ke model AI Vision, gambar KTP diolah terlebih dahulu menggunakan library `PIL` (Pillow) untuk meningkatkan kualitas keterbacaan teks:
* **Resizing (LANCZOS):** Ukuran gambar diperbesar 2x lipat menggunakan metode *Lanczos Resampling* agar detail huruf kecil pada KTP lebih tajam.
* **Enhancement Kontras:** Kontras gambar ditingkatkan sebesar 1.4x (`ImageEnhance.Contrast`) untuk memperjelas teks yang pudar atau terkena pantulan cahaya.
* **Base64 Encoding:** Gambar hasil olahan dikonversi ke format string *Base64* agar dapat dikirim secara aman melalui *payload* REST API OpenRouter.

### 2. Multimodal Vision AI (Classification & OCR)
Sistem memanfaatkan kombinasi model *Large Multimodal Model (LMM)* melalui gateway OpenRouter API:
* **Document Classification:** Memanfaatkan model `openai/gpt-4o-mini` atau `google/gemini-2.0-flash` dengan teknik *prompt engineering* berbasis JSON untuk mengklasifikasi apakah dokumen yang diunggah berupa KTP resmi Indonesia.
* **High-Precision Vision OCR:** Memanfaatkan model `openai/gpt-4o` (*High Detail Vision*) untuk mengekstrak 14 bidang data teks KTP (NIK, Nama, Tempat/Tgl Lahir, Alamat, RT/RW, Agama, Status, Pekerjaan, dll.) secara terstruktur dalam format **JSON**.

### 3. Deterministic NIK Business Rule Engine
Sistem menjalankan fungsi validasi matematis secara deterministik berdasarkan aturan baku formatur NIK Indonesia (16 digit: 6 digit wilayah, 6 digit tanggal lahir, 4 digit nomor urut):
* **Format & Numeric Check:** Memastikan NIK terdiri dari tepat 16 digit angka numerik.
* **Logika Jenis Kelamin & Tanggal Lahir (Aturan $+40$):** Untuk pemegang KTP **Perempuan**, digit tanggal lahir pada NIK secara resmi ditambah angka `40` (contoh: tanggal 15 menjadi 55). Engine validasi secara otomatis mengoreksi nilai tersebut ($day - 40$) untuk mencocokkan keabsahan antara tanggal lahir di NIK dan string `tempat_tgl_lahir`.

```python
# Potongan logika deterministik validasi NIK (app.py):
nik_day, nik_month, nik_year = int(nik[6:8]), int(nik), int(nik)
is_female = nik_day > 40
expected_gender = "PEREMPUAN" if is_female else "LAKI-LAKI"

actual_nik_day = nik_day - 40 if is_female else nik_day
dob_match = (
    actual_nik_day == parsed_dob.day
    and nik_month == parsed_dob.month
    and nik_year == (parsed_dob.year % 100)
)
```
### 4. Automated Data Masking (Perlindungan Data Pribadi / PII)
Guna mematuhi standar *Data Privacy* dan Perlindungan Data Pribadi (PDP), data sensitif disamarkan secara otomatis sebelum ditampilkan pada antarmuka Streamlit:
* **NIK Masking:** Menyisakan 4 digit pertama, sisanya diganti karakter `X` (contoh: `3471XXXXXXXXXXXX`).
* **Nama Masking:** Nama depan tetap utuh, kata berikutnya disamarkan (contoh: `DEWI T** L******`).
* **TTL & Alamat Masking:** Menyembunyikan tanggal lahir spesifik dan nomor rumah/RT/RW.

### 5. Relational Database Logging (SQLite)
Hasil ekstraksi data asli beserta metrik status validasinya disimpan ke dalam database relasional **SQLite3** (`ktp_database.db`) untuk kebutuhan *audit trail* dan pemantauan riwayat transaksi pada halaman *Database History*.

---

## 🚀 Cara Menjalankan Lokal

Berikut adalah langkah-langkah untuk menjalankan aplikasi ini secara lokal di laptop kamu:

```bash
# 1. Clone repository dari GitHub
git clone [https://github.com/dewitrilestari/Portofolio.git](https://github.com/dewitrilestari/Portofolio.git)

# 2. Masuk ke folder deployment proyek AI KTP
cd Portofolio/AI_KTP/Deployment

# 3. Install semua library/dependencies yang dibutuhkan
pip install -r requirements.txt

# 4. Buat file .env di dalam folder Deployment, lalu isi dengan API Key kamu:
# OPENROUTER_API_KEY="sk-or-v1-API_KEY_OPENROUTER_KAMU"

# 5. Jalankan aplikasi Streamlit
streamlit run app.py
```
