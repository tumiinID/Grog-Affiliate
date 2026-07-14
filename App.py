import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 1. KONFIGURASI KEAMANAN & DATA USER (UJI COBA MINGGU 1)
# Daftar password kustom untuk 5 penguji Anda
VALID_TOKENS = {
    "USER-01": "Penguji Satu",
    "USER-02": "Penguji Dua",
    "USER-03": "Penguji Tiga",
    "USER-04": "Penguji Empat",
    "USER-05": "Penguji Lima"
}

# Batasan Kunci Operasional Berbasis Kapasitas Riil
MAX_DAILY_GENERATE = 15 

# Inisialisasi basis data memori lokal server untuk melacak kuota harian
if "user_logs" not in st.session_state:
    st.session_state.user_logs = {}

# 2. SISTEM LOGIN PROTEKSI KATA SANDI
st.set_page_config(page_title="GROG AFFILIATE AI", layout="centered")

if "logged_in_user" not in st.session_state:
    st.title("🔒 Akses Terkunci - Uji Coba internal")
    st.write("Aplikasi ini berada dalam masa validasi tertutup. Masukkan token akses Anda:")
    
    token_input = st.text_input("Token Akses (Contoh: USER-01)", type="password")
    if st.button("Masuk Sistem"):
        if token_input in VALID_TOKENS:
            st.session_state.logged_in_user = token_input
            st.session_state.user_name = VALID_TOKENS[token_input]
            if token_input not in st.session_state.user_logs:
                st.session_state.user_logs[token_input] = []
            st.rerun()
        else:
            st.error("Token salah atau tidak terdaftar! Hubungi pemilik aplikasi.")
    st.stop()

# Jika sukses login, variabel user dikunci
current_user = st.session_state.logged_in_user
user_name = st.session_state.user_name

# Lacak jumlah penggunaan hari ini
today_str = datetime.now().strftime("%Y-%m-%d")
user_today_clicks = [log for log in st.session_state.user_logs[current_user] if log == today_str]
sisa_kuota = MAX_DAILY_GENERATE - len(user_today_clicks)

# 3. INTERFAS UTAMA (REPLIKASI FORM VISUAL)
st.title("Buat Konten Campaign. Satu Klik.")
st.write(f"Selamat bekerja, **{user_name}**. Jatah sisa generate harian Anda: **{sisa_kuota}/{MAX_DAILY_GENERATE}**")

st.markdown("---")

# Input File Utama
st.subheader("📦 Product Anchor")
product_file = st.file_uploader("Upload Foto Produk Utama (Max 5MB)", type=["jpg", "png", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    st.subheader("👤 Model")
    model_file = st.file_uploader("Upload Model (Opsional)", type=["jpg", "png", "jpeg"])
with col2:
    st.subheader("🖼️ Background")
    bg_file = st.file_uploader("Upload Background (Opsional)", type=["jpg", "png", "jpeg"])

st.markdown("---")

# Input Deskripsi
st.subheader("📝 Deskripsi Kampanye & Manfaat Produk")
campaign_desc = st.text_area("", placeholder="Contoh: Tanah kaplingan ukuran 12x24 meter, legalitas SHM, dekat jalan utama...")

# Pilihan Tone Gaya Bahasa
tone = st.selectbox("GAYA BAHASA (TONE)", ["Heboh & Energetic", "Santai & Edukatif", "Formal & Profesional", "Aesthetic & Emosional"])

# Pilihan Durasi Kelipatan Klip AI Video
durasi = st.selectbox(
    "TARGET DURASI VIDEO",
    [
        "15-20 Detik (Gabungan 4 Klip x 4-5 Detik)",
        "25-30 Detik (Gabungan 6 Klip x 4-5 Detik)",
        "50-60 Detik (Gabungan 12 Klip x 4-5 Detik)"
    ]
)

target_platform = st.selectbox("TARGET PLATFORM", ["TikTok & Reels (Rekomendasi)", "YouTube Shorts"])

st.markdown("---")

# 4. PROSES GENERATE DENGAN SISTEM KEAMANAN TAMENG ANTI-SPAM
st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #000000; color: white; font-size: 18px; font-weight: bold; border-radius: 30px; padding: 12px 0px; border: none;
    }
</style>
""", unsafe_allow_html=True)

if st.button("✨ Generate Campaign", use_container_width=True):
    # Cek kuota harian riil
    if len(user_today_clicks) >= MAX_DAILY_GENERATE:
        st.error(f"Maaf, kuota generate harian Anda ({MAX_DAILY_GENERATE} kali) sudah habis. Silakan kembali besok!")
    elif not campaign_desc:
        st.error("Deskripsi produk wajib diisi!")
    else:
        with st.spinner("Sedang memproses naskah rahasia..."):
            try:
                # Mengambil API KEY yang aman disembunyikan di server Streamlit Secrets
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                
                # Formula Prompt Rahasia Dapur Anda (Terkunci Aman)
                system_instruction = """Kamu adalah AI Copywriter berspesialisasi dalam konversi tinggi untuk TikTok Affiliate dan Reels. 
Hasilkan naskah video terstruktur berbasis durasi yang dipilih pengguna. Output wajib memisahkan antara 'Visual Prompt' (bahasa Inggris detail untuk Leonardo AI/Kling) dan 'Narasi/Voiceover' (bahasa Indonesia persuasif)."""
                
                model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
                
                user_prompt = f"Deskripsi Produk: {campaign_desc}\nTone: {tone}\nDurasi Pilihan: {durasi}\nPlatform: {target_platform}"
                
                # Proses data gambar jika diunggah
                # (Logika pemrosesan gambar multimodalan backend)
                
                response = model.generate_content(user_prompt)
                
                # Catat log sukses penggunaan kuota
                st.session_state.user_logs[current_user].append(today_str)
                
                st.success("Analisis Konten Sukses Dibuat!")
                st.markdown("### 📋 Hasil Rencana Alur Video Anda")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Koneksi server sibuk atau API Key belum dikonfigurasi. Eror: {str(e)}")
