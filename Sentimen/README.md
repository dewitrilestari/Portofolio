# 📊 Aplikasi Analisis Sentimen Pelemahan Rupiah

Aplikasi web untuk menganalisis sentimen publik (Positif, Netral, Negatif) terhadap isu pelemahan nilai tukar Rupiah menggunakan metode **Machine Learning (Logistic Regression)** dan pipeline NLP tingkat lanjut, dibangun dengan **Streamlit**.

🔗 **Live Demo:** https://dewi-portofolio-sentimen-analysis.streamlit.app/

[![Thumbnail Video YouTube](https://img.youtube.com/vi/2FPx1_CUzYQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=2FPx1_CUzYQ)
*Klik gambar di atas untuk melihat video YouTube sumber pengambilan data komentar (scraping).*

---

## 📌 Tentang Project

Project ini bertujuan untuk mengklasifikasikan opini, komentar, atau pendapat masyarakat terkait fenomena pelemahan Rupiah ke dalam tiga kategori sentimen. Aplikasi ini mengintegrasikan pipeline pembersihan teks (*text preprocessing*) yang kuat untuk menangani karakteristik teks media sosial bahasa Indonesia yang penuh dengan kata gaul (*slang*) dan singkatan.

Untuk mengatasi masalah ketidakseimbangan kelas (*imbalanced data*) di mana kelas mayoritas didominasi oleh sentimen Netral, model ini dilatih menggunakan pembobotan kelas yang seimbang (*balanced class weights*) agar sensitif terhadap kata-kata bermakna emosional kuat (negatif/positif).

---

## 🎯 Tujuan Analisis

* Mengklasifikasikan teks opini publik secara otomatis menjadi sentimen Positif, Netral, atau Negatif.
* Mengukur tingkat keyakinan (*Confidence Score*) model terhadap prediksi yang dihasilkan.
* Melakukan normalisasi teks kasual/slang menjadi kata baku untuk menjaga kualitas informasi.
* Memahami persepsi, kekhawatiran, atau respons masyarakat terhadap kondisi makroekonomi dalam negeri.

---

## 🗂️ Struktur Project

```text
Sentimen/
├── Deployment/
│   ├── app.py                  # Aplikasi Utama Streamlit
│   ├── model_sentimen.pkl      # Model Logistic Regression (Trained)
│   └── vectorizer.pkl          # CountVectorizer (Trained)
├── requirements.txt            # Dependency Library (Streamlit, Sastrawi, dll)
└── README.md                   # Dokumentasi Proyek
```

---

## ⚙️ Fitur Dashboard

| Fitur                      | Keterangan                                                         |
| -------------------------- | ------------------------------------------------------------------ |
| Sentiment Classifier       | Memprediksi label sentimen (POSITIF, NETRAL, NEGATIF) secara tepat |
| Confidence Indicator       | Menampilkan skor kepastian prediksi model dengan Progress Bar      |
| Custom Slang Normalizer    | Kamus pemetaan kata gaul/umpatan komprehensif menjadi kata baku    |
| Sastrawi Stemmer Pipeline  | Pemotongan imbuhan secara real-time menjadi kata dasar otomatis    |
| Responsive Layout          | Penataan visual berbasis kolom kiri-kanan yang modern dan rapi     |

---

## 📊 Metode yang Digunakan

### 1. Advanced Text Preprocessing & Tokenization

* Slang Normalization: Mengubah variasi kata gaul, singkatan, ataupun umpatan ('anjer', 'ajggg', 'njing', 'bangsyattttt') menjadi representasi kata baku penunjuk emosi negatif terpusat ('sial').

* Custom Stopwords Removal: Menyaring kata-kata tidak bermakna dengan tetap mempertahankan kata negasi krusial seperti ('tidak', 'jangan', 'bukan') agar makna sentimen tidak terbalik.

* Real-time Stemming (Sastrawi): Merubah kata berimbuhan menjadi kata dasarnya sebelum diumpankan ke model statistik.

### 2. Logistic Regression (Balanced)

* Menggunakan algoritma linear terbobot untuk memetakan probabilitas teks ke dalam multi-kelas.

* Solusi mengatasi imbalanced data (Positif ~10%, Netral ~48%, Negatif ~42%)
lr = LogisticRegression(class_weight='balanced', random_state=42)

## 🚀 Cara Menjalankan Lokal

```bash
# Clone repository
git clone [https://github.com/dewitrilestari/Portofolio.git](https://github.com/dewitrilestari/Portofolio.git)

# Masuk ke folder project
cd Portofolio/Sentimen/Deployment

# Install dependency
pip install -r requirements.txt

# Jalankan aplikasi
streamlit run app.py
```

Aplikasi lokal akan berjalan secara otomatis di browser kamu melalui port default Streamlit.

---

## 🌐 Deploy

Aplikasi ini dideploy menggunakan Streamlit Community Cloud yang terintegrasi langsung dengan repositori GitHub sehingga setiap pembaruan model atau UI dapat langsung dinikmati oleh pengguna secara online tanpa instalasi mandiri.

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* NumPy
* Scikit-Learn
* Sastrawi

---

## 📈 Manfaat Bisnis

* Menjadi alat monitoring reputasi/sentimen publik terhadap kebijakan moneter atau ekonomi negara.
* Menyediakan pipeline pembersihan teks bahasa Indonesia yang adaptif terhadap bahasa kasual internet.
* Memahami perilaku pembelian pelanggan.
* Sebagai referensi portofolio terapan dari konsep Data Science, Natural Language Processing (NLP), dan Deployment Application.

---

---

## ⚠️ Catatan Penting

* **Batasan Model:** Hasil prediksi sangat bergantung pada variasi kata yang ada pada dataset *training*. Jika pengguna memasukkan kata analogi baru yang belum pernah dipelajari model, akurasinya mungkin akan menurun.
* **Penanganan Efek Stemming:** Penggunaan Sastrawi Stemmer secara *real-time* di Streamlit sangat krusial untuk menyamakan bentuk kata input dengan isi bobot data latih di Google Colab.
* **Tujuan Proyek:** Proyek ini dibangun murni untuk keperluan portofolio, pembelajaran *Natural Language Processing* (NLP), dan analisis sentimen berbasis teks berbahasa Indonesia kasual.
