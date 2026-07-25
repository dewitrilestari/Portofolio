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

## ⚙️ Fitur Dashboard

<table>
  <thead>
    <tr>
      <th>Nama Fitur</th>
      <th>Tampilan / Representasi Visual</th>
      <th>Keterangan & Detail Teknis</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Document Classification</b></td>
      <td>Status Badge (<i>KTP / Bukan KTP</i>)</td>
      <td>Mengidentifikasi apakah gambar yang diunggah adalah KTP Indonesia menggunakan model Multimodal Vision (<code>openai/gpt-4o-mini</code> / <code>google/gemini-2.0-flash</code>).</td>
    </tr>
    <tr>
      <td><b>High-Precision Vision OCR</b></td>
      <td>Tabel Data Format JSON</td>
      <td>Mengekstrak 14 bidang teks KTP (NIK, Nama, TTL, Alamat, RT/RW, Agama, dll.) secara terstruktur dengan tingkat akurasi tinggi menggunakan <code>openai/gpt-4o</code>.</td>
    </tr>
    <tr>
      <td><b>Deterministic Business Rule Validation</b></td>
      <td>Tabel Status Per Aturan (<i>VALID / INVALID</i>)</td>
      <td>Menguji keabsahan NIK: pengecekan 16 digit angka, pemutakhiran tanggal lahir, serta validasi pola jenis kelamin (pria vs wanita di mana tanggal +40).</td>
    </tr>
    <tr>
      <td><b>Automated Data Masking (Privacy Protection)</b></td>
      <td>Teks Disamarkan (<i>Contoh: 3471XXXXXXXXXXXX</i>)</td>
      <td>Menyamarkan data sensitif pengguna secara otomatis sebelum dirender ke layar untuk menjaga privasi di repositori publik.</td>
    </tr>
    <tr>
      <td><b>SQLite History Logging</b></td>
      <td>Halaman <i>Database History</i></td>
      <td>Menyimpan data hasil ekstraksi ke database SQLite (<code>ktp_database.db</code>) dan menampilkan tabel riwayat transaksi secara terorganisir.</td>
    </tr>
    <tr>
      <td><b>Secure Credentials Management</b></td>
      <td>Konfigurasi Secrets / <code>.env</code></td>
      <td>Mengamankan API Key menggunakan Streamlit Secrets (<code>st.secrets</code>) dan file <code>.env</code> yang dilindungi oleh <code>.gitignore</code>.</td>
    </tr>
    <tr>
      <td><b>Professional Branding Footer</b></td>
      <td>Bagian Terbawah Aplikasi</td>
      <td>Menyediakan tautan portofolio berupa ikon tautan langsung menuju profil <b>GitHub</b> dan <b>LinkedIn</b> pembuat aplikasi.</td>
    </tr>
  </tbody>
</table>
