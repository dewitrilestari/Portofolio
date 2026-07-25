import base64
from datetime import datetime
import io
import json
import sqlite3
import pandas as pd
from PIL import Image, ImageEnhance
import requests
import streamlit as st

# ==========================================
# 🔑 KONFIGURASI API KEY & DATABASE
# ==========================================
OPENROUTER_API_KEY = (
    "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"
)
DB_NAME = "ktp_database.db"

# Page Config Streamlit
st.set_page_config(
    page_title="Sistem OCR KTP & Validasi AI", page_icon="🪪", layout="wide"
)


# ==========================================
# 🗄️ DATABASE FUNCTIONS (SQLITE)
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ktp_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nik TEXT,
        nama TEXT,
        tempat_tgl_lahir TEXT,
        jenis_kelamin TEXT,
        agama TEXT,
        alamat TEXT,
        rt TEXT,
        rw TEXT,
        kelurahan TEXT,
        kecamatan TEXT,
        status_perkawinan TEXT,
        pekerjaan TEXT,
        kewarganegaraan TEXT,
        berlaku_hingga TEXT,
        overall_status TEXT,
        validation_details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def save_ktp_record(ocr_data: dict, validation_res: dict) -> int:
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO ktp_records (
        nik, nama, tempat_tgl_lahir, jenis_kelamin, agama, alamat,
        rt, rw, kelurahan, kecamatan, status_perkawinan, pekerjaan,
        kewarganegaraan, berlaku_hingga, overall_status, validation_details
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            ocr_data.get("nik", ""),
            ocr_data.get("nama", ""),
            ocr_data.get("tempat_tgl_lahir", ""),
            ocr_data.get("jenis_kelamin", ""),
            ocr_data.get("agama", ""),
            ocr_data.get("alamat", ""),
            ocr_data.get("rt", ""),
            ocr_data.get("rw", ""),
            ocr_data.get("kelurahan", ""),
            ocr_data.get("kecamatan", ""),
            ocr_data.get("status_perkawinan", ""),
            ocr_data.get("pekerjaan", ""),
            ocr_data.get("kewarganegaraan", ""),
            ocr_data.get("berlaku_hingga", ""),
            validation_res.get("overall_status", "INVALID"),
            json.dumps(validation_res, ensure_ascii=False),
        ),
    )
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_all_ktp_records() -> list:
    init_db()
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ktp_records ORDER BY created_at DESC")
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


# ==========================================
# 🧠 AI & PROCESSING FUNCTIONS
# ==========================================
def preprocess_image_bytes(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    w, h = img.size
    img = img.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.4)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def classify_document(image_bytes: bytes) -> bool:
    base64_image = preprocess_image_bytes(image_bytes)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    prompt_text = 'Apakah gambar ini KTP Indonesia? Jawab HANYA JSON: {"is_ktp": true} atau {"is_ktp": false}'

    candidate_models = [
        "google/gemini-2.0-flash-exp:free",
        "openai/gpt-4o-mini",
    ]

    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "response_format": {"type": "json_object"},
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                raw = res.json()["choices"][0]["message"]["content"]
                return json.loads(raw).get("is_ktp", False)
        except Exception:
            continue
    return False


def extract_ktp_ocr(image_bytes: bytes) -> dict:
    base64_image = preprocess_image_bytes(image_bytes)
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt_text = """
    Kamu adalah sistem OCR KTP Indonesia. Ekstrak data KTP ini ke JSON.
    NIK Wajib 16 digit. Lakukan verifikasi digit NIK dengan 'tempat_tgl_lahir' dan 'jenis_kelamin'.
    
    Format JSON wajib:
    {
        "nik": "", "nama": "", "tempat_tgl_lahir": "", "jenis_kelamin": "",
        "agama": "", "alamat": "", "rt": "", "rw": "", "kelurahan": "",
        "kecamatan": "", "status_perkawinan": "", "pekerjaan": "",
        "kewarganegaraan": "", "berlaku_hingga": ""
    }
    """

    payload = {
        "model": "openai/gpt-4o",
        "temperature": 0.0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        if res.status_code == 200:
            raw = res.json()["choices"][0]["message"]["content"]
            return json.loads(raw)
    except Exception as e:
        st.error(f"Error OCR: {e}")
    return {}


def validate_ktp_business_rules(data: dict) -> dict:
    validation_summary = {
        "nik_length": {"valid": False, "message": ""},
        "nik_is_numeric": {"valid": False, "message": ""},
        "dob_format": {"valid": False, "message": ""},
        "gender_match": {"valid": False, "message": ""},
        "dob_match": {"valid": False, "message": ""},
        "overall_status": "INVALID",
    }

    nik = str(data.get("nik", "")).strip()
    tempat_tgl_lahir = str(data.get("tempat_tgl_lahir", "")).strip()
    jenis_kelamin = str(data.get("jenis_kelamin", "")).strip().upper()

    validation_summary["nik_is_numeric"]["valid"] = nik.isdigit()
    validation_summary["nik_is_numeric"][
        "message"
    ] = "NIK berisi angka." if nik.isdigit() else "NIK mengandung non-angka."

    validation_summary["nik_length"]["valid"] = len(nik) == 16
    validation_summary["nik_length"][
        "message"
    ] = "Panjang NIK 16 digit." if len(nik) == 16 else f"Panjang NIK {len(nik)} digit."

    tgl_str = (
        tempat_tgl_lahir.split(",")[-1].strip()
        if "," in tempat_tgl_lahir
        else tempat_tgl_lahir
    )
    parsed_dob = None
    try:
        parsed_dob = datetime.strptime(tgl_str, "%d-%m-%Y")
        validation_summary["dob_format"]["valid"] = True
        validation_summary["dob_format"][
            "message"
        ] = f"Format tanggal valid ({tgl_str})."
    except ValueError:
        validation_summary["dob_format"][
            "message"
        ] = f"Format tanggal '{tgl_str}' salah."

    if len(nik) == 16 and nik.isdigit() and parsed_dob:
        nik_day, nik_month, nik_year = (
            int(nik[6:8]),
            int(nik[8:10]),
            int(nik[10:12]),
        )
        is_female = nik_day > 40
        expected_gender = "PEREMPUAN" if is_female else "LAKI-LAKI"

        validation_summary["gender_match"]["valid"] = (
            jenis_kelamin == expected_gender
        )
        validation_summary["gender_match"][
            "message"
        ] = f"Jenis kelamin '{jenis_kelamin}' sesuai NIK."

        actual_nik_day = nik_day - 40 if is_female else nik_day
        dob_match = (
            actual_nik_day == parsed_dob.day
            and nik_month == parsed_dob.month
            and nik_year == (parsed_dob.year % 100)
        )
        validation_summary["dob_match"]["valid"] = dob_match
        validation_summary["dob_match"][
            "message"
        ] = "Tanggal lahir di NIK cocok dengan tempat_tgl_lahir."

    all_passed = all(
        v["valid"]
        for k, v in validation_summary.items()
        if k != "overall_status"
    )
    if all_passed:
        validation_summary["overall_status"] = "VALID"

    return validation_summary


# ==========================================
# 🎛️ STREAMLIT INTERFACE (SIDEBAR NAVIGATION)
# ==========================================
init_db()

st.sidebar.title("📌 Navigasi")
page = st.sidebar.radio(
    "Pilih Halaman:",
    ["Home", "Upload & Process Image", "Database History"],
)

# ------------------------------------------
# 1. HALAMAN HOME
# ------------------------------------------
if page == "Home":
    st.title("🪪 Sistem Pembaca & Validasi KTP Indonesia")
    st.markdown("---")

    st.subheader("📝 Penjelasan Singkat")
    st.write(
        """
        Aplikasi ini memanfaatkan teknologi **AI Vision** mutakhir untuk melakukan ekstraksi data KTP secara otomatis 
        dan menjalankan **Business Rule Validation** resmi untuk memastikan keabsahan nomor NIK, tanggal lahir, dan jenis kelamin.
        """
    )

    st.subheader("🤖 Informasi Model AI yang Digunakan")
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **1. AI Classification Model**
        * **Model**: `google/gemini-2.0-flash-exp` / `openai/gpt-4o-mini`
        * **Fungsi**: Memverifikasi apakah dokumen yang diunggah berupa KTP Indonesia.
        """)
    with col2:
        st.success("""
        **2. Vision OCR Model**
        * **Model**: `openai/gpt-4o` (High-Detail Vision)
        * **Fungsi**: Mengekstrak bidang teks KTP menjadi format JSON terstruktur dengan tingkat presisi tinggi.
        """)

# ------------------------------------------
# 2. HALAMAN UPLOAD & PROCESS IMAGE
# ------------------------------------------
elif page == "Upload & Process Image":
    st.title("📤 Upload Image & Process OCR")
    st.write(
        "Unggah foto KTP Indonesia untuk menguji klasifikasi, ekstraksi OCR, dan validasi data."
    )
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Pilih File Gambar KTP (JPG / PNG / JPEG)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()

        col_img, col_res = st.columns([1, 1.5])

        with col_img:
            st.image(
                image_bytes,
                caption="Gambar KTP Diunggah",
                use_container_width=True,
            )

        with col_res:
            st.subheader("🔍 Classification Result")
            with st.spinner("Menganalisis dokumen dengan AI Vision..."):
                is_ktp = classify_document(image_bytes)

            if is_ktp:
                st.success("✅ **Prediction**: KTP Indonesia")
                st.markdown("---")

                # OCR Extraction
                st.subheader("📄 OCR Result")
                with st.spinner("Mengekstrak data teks KTP..."):
                    ocr_data = extract_ktp_ocr(image_bytes)

                # Format Tampilan Tabel OCR (Field | Value)
                df_ocr = pd.DataFrame(
                    [
                        {"Field": k.replace("_", " ").upper(), "Value": v}
                        for k, v in ocr_data.items()
                    ]
                )
                st.table(df_ocr)

                st.markdown("---")

                # Validation Result
                st.subheader("🛡️ Validation Result")
                validation_res = validate_ktp_business_rules(ocr_data)

                # Tabel Status Validasi Per Bidang
                val_rows = [
                    {
                        "Bidang / Aturan": "Panjang NIK (16 Digit)",
                        "Status": (
                            "✅ VALID"
                            if validation_res["nik_length"]["valid"]
                            else "❌ INVALID"
                        ),
                        "Keterangan": validation_res["nik_length"]["message"],
                    },
                    {
                        "Bidang / Aturan": "Karakter NIK (Numeric)",
                        "Status": (
                            "✅ VALID"
                            if validation_res["nik_is_numeric"]["valid"]
                            else "❌ INVALID"
                        ),
                        "Keterangan": validation_res["nik_is_numeric"][
                            "message"
                        ],
                    },
                    {
                        "Bidang / Aturan": "Format Tanggal Lahir",
                        "Status": (
                            "✅ VALID"
                            if validation_res["dob_format"]["valid"]
                            else "❌ INVALID"
                        ),
                        "Keterangan": validation_res["dob_format"]["message"],
                    },
                    {
                        "Bidang / Aturan": "Kesesuaian Jenis Kelamin",
                        "Status": (
                            "✅ VALID"
                            if validation_res["gender_match"]["valid"]
                            else "❌ INVALID"
                        ),
                        "Keterangan": validation_res["gender_match"]["message"],
                    },
                    {
                        "Bidang / Aturan": "Kesesuaian Tanggal Lahir vs NIK",
                        "Status": (
                            "✅ VALID"
                            if validation_res["dob_match"]["valid"]
                            else "❌ INVALID"
                        ),
                        "Keterangan": validation_res["dob_match"]["message"],
                    },
                ]
                st.table(pd.DataFrame(val_rows))

                # Ringkasan Status Akhir
                if validation_res["overall_status"] == "VALID":
                    st.balloons()
                    st.success("🎉 **STATUS AKHIR DATA KTP: VALID**")
                else:
                    st.error("⚠️ **STATUS AKHIR DATA KTP: INVALID**")

                # Simpan otomatis ke SQLite
                saved_id = save_ktp_record(ocr_data, validation_res)
                st.caption(
                    f"💾 Data berhasil disimpan otomatis ke SQLite (Record ID: {saved_id})"
                )

            else:
                st.error("❌ **Prediction**: Bukan KTP Indonesia")
                st.warning(
                    "Proses dihentikan karena dokumen yang diunggah tidak terdeteksi sebagai KTP."
                )

# ------------------------------------------
# 3. HALAMAN DATABASE HISTORY
# ------------------------------------------
elif page == "Database History":
    st.title("🗄️ Database History")
    st.write(
        "Menampilkan seluruh riwayat hasil ekstraksi KTP yang tersimpan di SQLite."
    )
    st.markdown("---")

    records = get_all_ktp_records()

    if records:
        df_records = pd.DataFrame(records)

        # Reorder / Select Kolom Tampilan
        columns_to_show = [
            "id",
            "nik",
            "nama",
            "tempat_tgl_lahir",
            "jenis_kelamin",
            "alamat",
            "overall_status",
            "created_at",
        ]
        df_display = df_records[columns_to_show]

        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Belum ada data KTP tersimpan di database.")