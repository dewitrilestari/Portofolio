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
    st.subheader("Hasil Analisis:")
    
    # Memberi warna box berdasarkan hasil prediksi sentimen
    if prediksi.lower() == 'positive' or prediksi == 'positif':
        st.success(f"**Sentimen:** {prediksi.upper()}")
    elif prediksi.lower() == 'negative' or prediksi == 'negatif':
        st.error(f"**Sentimen:** {prediksi.upper()}")
    else:
        st.warning(f"**Sentimen:** {prediksi.upper()}")
        
    st.info(f"**💡 Confidence Score:** {confidence_score:.2f}%")
    # Teks penjelasan singkat tambahan yang kamu inginkan:
    st.caption(
        f"**Maksud Nilai:** Model memiliki tingkat keyakinan sebesar **{confidence_score:.2f}%** "
        f"bahwa kalimat di atas termasuk ke dalam kategori sentimen **{prediksi.upper()}** "
        f"berdasarkan pola kata yang telah dipelajari pada data training."
    )
