# 📊 Aplikasi Analisis Sentimen Pelemahan Rupiah

Aplikasi web untuk menganalisis sentimen publik (Positif, Netral, Negatif) terhadap isu pelemahan nilai tukar Rupiah menggunakan metode **Machine Learning (Logistic Regression)** dan pipeline NLP tingkat lanjut, dibangun dengan **Streamlit**.

🔗 **Live Demo:** https://dewi-portofolio-sentimen-analysis.streamlit.app/

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
