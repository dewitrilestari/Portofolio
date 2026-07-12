import pickle
import pandas as pd
import streamlit as st
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# ==========================================
# 1. LOAD MODEL (lr) & VECTORIZER (CountVectorizer)
# ==========================================
with open('Sentimen/Deployment/model_sentimen.pkl', 'rb') as f:
    lr = pickle.load(f)

with open('Sentimen/Deployment/vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# ==========================================
# 2. DEFINISIKAN STOPWORDS & PREPROCESSING
# ==========================================
# Set custom stopwords yang sudah kita seragamkan sebelumnya
custom_stopwords = {
    'a', 'aaaclan', 'adalah', 'agar', 'ah', 'ahhh', 'akan', 'aku', 'allah', 
    'yang', 'ya', 'yah', 'yoi', 'yz'  # ... teruskan sesuai daftar lengkapmu
}

def clean_text(text):
    # Ubah ke huruf kecil dan pecah menjadi kata
    tokens = text.lower().split()
    # Hilangkan kata yang termasuk dalam stopword
    cleaned_tokens = [word for word in tokens if word not in custom_stopwords]
    # Gabungkan kembali menjadi satu string kalimat
    return " ".join(cleaned_tokens)

# ==========================================
# 3. INTERFACE STREAMLIT
# ==========================================
st.title("📊 Aplikasi Analisis Sentimen Pelemahan Rupiah")
# ==========================================
# 1. PENAMBAHAN SIDEBAR (INFORMASI PROYEK)
# ==========================================
with st.sidebar:
    st.markdown("## 📊 Detail Proyek")
    st.markdown("### 📌 Tentang Aplikasi")
    st.write(
        "Aplikasi ini dirancang untuk menganalisis dan mengklasifikasikan "
        "opini serta sentimen masyarakat mengenai fenomena pelemahan nilai tukar Rupiah."
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Spesifikasi Model")
    
    # Menampilkan F1-Score sebagai metrik utama yang lebih kredibel untuk imbalanced data
    st.markdown("""
    | Komponen | Detail Teknis |
    | :--- | :--- |
    | **Sumber Data** |[Komentar YouTube](https://www.youtube.com/watch?v=2FPx1_CUzYQ)|
    | **Jumlah Data** | ~9,000 Baris Teks |
    | **Algoritma** | Logistic Regression |
    | **Fitur Ekstraksi**| CountVectorizer |
    | **F1-Score Model** | **66.5% (0.665)** |
    """)

st.write("Masukkan kalimat pendapat atau komentar untuk memprediksi sentimennya.")

# Menerima input dari user
user_input = st.text_input("Ketik kalimat di sini:", placeholder="Contoh: Rupiah melemah bikin pusing...")

if user_input:
    # 1. Ubah teks jadi huruf kecil & bersihkan dari stopwords
    text_cleaned = clean_text(user_input)
    
    # 2. Lakukan Stemming pada teks yang SUDAH BERSIH
    text_stemmed = stemmer.stem(text_cleaned)
    
    # 3. Masukkan VARIABEL text_stemmed (Umpankan kata dasarnya ke vectorizer!)
    text_vector = vectorizer.transform([text_stemmed])
    
    # 4. Prediksi Sentimen menggunakan model Logistic Regression (lr)
    prediksi = lr.predict(text_vector)[0]
    
    # 5. Hitung Confidence Score (Probabilitas)
    probabilitas = lr.predict_proba(text_vector)
    confidence_score = max(probabilitas[0]) * 100
    
    # 6. Tampilkan Hasil Ke User
    st.markdown("---")
    st.markdown("### 🔍 Hasil Analisis")
    
    # Membuat 2 kolom untuk menyejajarkan hasil
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Kategori Sentimen**")
        if prediksi.lower() == 'positive' or prediksi == 'positif':
            st.markdown(
                "<div style='background-color: #d4edda; color: #155724; padding: 15px; "
                "border-radius: 10px; border-left: 5px solid #28a745; font-size: 20px; font-weight: bold;'>"
                "🟢 POSITIF"
                "</div>", 
                unsafe_allow_html=True
            )
        elif prediksi.lower() == 'negative' or prediksi == 'negatif':
            st.markdown(
                "<div style='background-color: #f8d7da; color: #721c24; padding: 15px; "
                "border-radius: 10px; border-left: 5px solid #dc3545; font-size: 20px; font-weight: bold;'>"
                "🔴 NEGATIF"
                "</div>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='background-color: #fff3cd; color: #856404; padding: 15px; "
                "border-radius: 10px; border-left: 5px solid #ffc107; font-size: 20px; font-weight: bold;'>"
                "🟡 NETRAL"
                "</div>", 
                unsafe_allow_html=True
            )
            
    with col2:
        st.markdown("**Tingkat Keyakinan Model**")
        # Menampilkan metrik besar yang bersih
        st.metric(label="Confidence Score", value=f"{confidence_score:.2f}%")
        # Menambahkan progress bar visual di bawah nilai persentase
        st.progress(int(confidence_score))

    # Teks penjelasan di bagian bawah dengan box informasi yang rapi
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        f"**Maksud Nilai:** Model memiliki tingkat keyakinan sebesar **{confidence_score:.2f}%** "
        f"bahwa kalimat di atas termasuk ke dalam kategori sentimen **{prediksi.upper()}** "
        f"berdasarkan pola kata yang telah dipelajari pada data training."
    )

# ==========================================
# 2. PENAMBAHAN FOOTER (PROFESIONAL BRANDING)
# ==========================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")

# Menggunakan HTML + CSS agar posisi footer berada di tengah dan rapi
st.markdown(
    """
    <div style='text-align: center; font-size: 14px; color: #6c757d; line-height: 1.6;'>
        Developed by <b>Dewi Tri Lestari</b> <br>
        <a href="https://github.com/dewitrilestari/Portofolio/edit/main/Sentimen/" target="_blank" style="text-decoration: none; color: #0366d6; font-weight: bold;">💻 GitHub</a> | 
        <a href="https://www.linkedin.com/in/dewitrilestari/" target="_blank" style="text-decoration: none; color: #0a66c2; font-weight: bold;">🌐 LinkedIn</a>
    </div>
    """, 
    unsafe_allow_html=True
)
