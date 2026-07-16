import streamlit as st
import pandas as pd
import joblib
import sklearn

# Set konfigurasi halaman agar terlihat profesional
st.set_page_config(
    page_title="Rekomendasi Retail - Collaborative Filtering",
    page_icon="🛍️",
    layout="wide"
)

# 1. LOAD FILE INPUT MENGGUNAKAN JOBLIB
@st.cache_resource
def load_model_data():
    product_corr = joblib.load('product_corr.joblib')
    df_master_cf = joblib.load('df_master_cf.joblib')
    return product_corr, df_master_cf

try:
    product_corr, df_master_cf = load_model_data()
    daftar_produk = sorted(list(product_corr.columns))
except FileNotFoundError:
    st.error("❌ File 'product_corr.joblib' atau 'df_master_cf.joblib' tidak ditemukan di direktori. Pastikan sudah di-upload!")
    st.stop()

# 2. FUNGSI REKOMENDASI COLLABORATIVE FILTERING
def recommend_retail_cf(target_nama_produk, n=10):
    target_nama_produk = str(target_nama_produk).strip().upper()
    
    if target_nama_produk not in product_corr.columns:
        return None
        
    similar_products = product_corr[target_nama_produk].sort_values(ascending=False).iloc[1:n+1]
    
    result = pd.DataFrame({
        'Nama Produk Rekomendasi': similar_products.index,
        'Pearson Correlation': similar_products.values
    })
    
    # Mapping kategori dilakukan saat nama produk masih UPPERCASE
    mapping_cat = dict(zip(df_master_cf['nama_produk'], df_master_cf['product_category']))
    result['Kategori Produk'] = result['Nama Produk Rekomendasi'].map(mapping_cat)
    
    # Mengubah nama produk menjadi lowercase
    result['Nama Produk Rekomendasi'] = result['Nama Produk Rekomendasi'].str.lower()
    
    result['Alasan Rekomendasi'] = f'Pelanggan yang membeli "{target_nama_produk}" juga cenderung membeli produk ini.'
    
    # Mengembalikan dataframe tanpa Stock Code
    return result[['Nama Produk Rekomendasi', 'Kategori Produk', 'Pearson Correlation', 'Alasan Rekomendasi']]

# 3. INTERFACE APLIKASI STREAMLIT
st.title("🛍️ Sistem Rekomendasi Produk Retail")
st.subheader("Metode: Item-to-Item Collaborative Filtering (Pearson Correlation)")

# Menambahkan penjelasan metode
with st.expander("ℹ️ Apa itu metode ini?"):
    st.markdown("""
    * **Collaborative Filtering (Item-to-Item):** Teknik untuk memberikan rekomendasi produk berdasarkan pola perilaku pengguna di masa lalu. Jika banyak pelanggan membeli produk A dan B secara bersamaan, maka sistem menganggap produk tersebut 'berhubungan'.
    * **Pearson Correlation:** Metode statistik untuk mengukur hubungan antara dua produk (-1 hingga 1):
        * **Mendekati 1 (Positif):** Produk sangat sering dibeli bersamaan (sangat disarankan untuk rekomendasi).
        * **Mendekati 0 (Netral):** Tidak ada hubungan pola pembelian yang signifikan antar produk.
        * **Mendekati -1 (Negatif):** Hubungan berlawanan; jika pelanggan membeli satu produk, mereka jarang membeli produk lainnya (produk saling menggantikan).
    """)

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    pilihan_produk = st.selectbox(
        "Cari atau Pilih Nama Produk Target:",
        options=daftar_produk,
        index=0
    )

with col2:
    jumlah_rekomendasi = st.slider("Jumlah Rekomendasi yang Ditampilkan:", min_value=1, max_value=20, value=10)

if st.button("🚀 Generate Rekomendasi", type="primary"):
    with st.spinner("Mencari produk serupa di database..."):
        hasil = recommend_retail_cf(pilihan_produk, n=jumlah_rekomendasi)
        
        if hasil is not None and not hasil.empty:
            st.success(f"🎯 Berhasil menemukan {len(hasil)} rekomendasi teratas untuk produk: **{pilihan_produk}**")
            
            # Menampilkan dataframe dengan lebar kolom alasan yang disesuaikan
            st.dataframe(
                hasil.style.format({'Pearson Correlation': '{:.4f}'}), 
                use_container_width=False, 
                column_config={
                    "Alasan Rekomendasi": st.column_config.TextColumn(
                        "Alasan Rekomendasi",
                        width=600  
                    )
                }
            )
        else:
            st.warning("Tidak ada rekomendasi yang cocok ditemukan untuk produk tersebut.")
