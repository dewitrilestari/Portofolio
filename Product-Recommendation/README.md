# 🛒 Dashboard Association Rules Recommendation

Aplikasi web untuk menganalisis pola pembelian pelanggan dan menghasilkan rekomendasi produk menggunakan kombinasi metode **Content-Based Filtering** dan **Collaborative Filtering**, dibangun dengan **Streamlit**.

🔗 **Live Demo:** https://aappciation-rules-b4ttm5iv5g275seryqwwpj.streamlit.app/

---

## 📌 Tentang Project

Project ini bertujuan mengidentifikasi hubungan antar produk yang sering dibeli pelanggan serta memberikan rekomendasi produk yang relevan berdasarkan histori transaksi retail.

Aplikasi menggabungkan tiga pendekatan rekomendasi:

* **Content-Based Filtering** untuk merekomendasikan produk dengan karakteristik serupa.
* **Collaborative Filtering** untuk merekomendasikan produk berdasarkan perilaku pelanggan yang mirip.

Dataset yang digunakan berasal dari transaksi retail online yang berisi informasi invoice, produk, kuantitas, harga, dan pelanggan.

---

## 🎯 Tujuan Analisis

* Menemukan produk yang sering dibeli bersama.
* Memberikan rekomendasi produk secara otomatis.
* Membantu strategi cross-selling dan bundling produk.
* Mengidentifikasi preferensi pelanggan berdasarkan histori pembelian.

---

## 🗂️ Struktur Project

```text
assorules/
├── app.py                  # Aplikasi Streamlit
├── model/
│   ├── df_master_cf
│   ├── product_corr
├── requirements.txt
└── README.md
```

---

## ⚙️ Fitur Dashboard

| Fitur                   | Keterangan                                         |
| ----------------------- | -------------------------------------------------- |
| Product Recommendation  | Rekomendasi produk berdasarkan produk yang dipilih |
| Content-Based Filtering | Menampilkan produk dengan karakteristik serupa     |
| Collaborative Filtering | Menampilkan produk yang disukai pelanggan serupa   |
| Market Basket Analysis  | Analisis kombinasi produk dalam satu transaksi     |
| Interactive Dashboard   | Visualisasi dan eksplorasi data secara interaktif  |

---

## 📊 Metode yang Digunakan

### 1. Content-Based Filtering

Merekomendasikan produk berdasarkan kemiripan atribut atau karakteristik produk.

Contoh:

```text
KNITTED UNION FLAG HOT WATER BOTTLE
→ WHITE SKULL HOT WATER BOTTLE
```

### 2. Collaborative Filtering

Merekomendasikan produk berdasarkan pola pembelian pelanggan lain yang memiliki perilaku serupa.

Contoh:

```text
RED WOOLLY HOTTIE WHITE HEART
→ SCOTTIE DOG HOT WATER BOTTLE
```

## 🚀 Cara Menjalankan Lokal

```bash
# Clone repository
git clone https://github.com/dewitrilestari/Association-Rules.git

# Masuk ke folder project
cd Association-Rules

# Install dependency
pip install -r requirements.txt

# Jalankan aplikasi
streamlit run app.py
```

Aplikasi akan berjalan di:

```text
https://aappciation-rules-b4ttm5iv5g275seryqwwpj.streamlit.app/
```

---

## 🌐 Deploy

Aplikasi dideploy menggunakan Streamlit Community Cloud sehingga dapat diakses secara online melalui browser tanpa instalasi tambahan.

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* NumPy
* Scikit-Learn
* Collaborative Filtering

---

## 📈 Manfaat Bisnis

* Meningkatkan peluang cross-selling.
* Membantu penyusunan paket bundling produk.
* Memahami perilaku pembelian pelanggan.
* Mendukung pengambilan keputusan pemasaran berbasis data.
* Mengoptimalkan strategi promosi dan penempatan produk.

---

## ⚠️ Catatan

* Hasil rekomendasi bergantung pada kualitas dan jumlah data transaksi yang tersedia.
* Tidak semua produk akan menghasilkan association rules yang kuat.
* Project ini dibuat untuk tujuan pembelajaran data mining, machine learning, dan sistem rekomendasi pada data retail.
