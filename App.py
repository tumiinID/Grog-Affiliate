import streamlit as st
import google.generativeai as genai
from datetime import datetime
from PIL import Image

# 1. KONFIGURASI KEAMANAN & DATA USER
VALID_TOKENS = {
    "USER-01": "Penguji Satu",
    "USER-02": "Penguji Dua",
    "USER-03": "Penguji Tiga",
    "USER-04": "Penguji Empat",
    "USER-05": "Penguji Lima"
}

MAX_DAILY_GENERATE = 15 

if "user_logs" not in st.session_state:
    st.session_state.user_logs = {}

st.set_page_config(page_title="GROG AFFILIATE AI", layout="centered")

if "logged_in_user" not in st.session_state:
    st.title("🔒 Akses Terkunci - Uji Coba Internal")
    st.write("Aplikasi ini berada dalam masa validasi tertutup. Masukkan token akses Anda:")
    
    token_input = st.text_input("Token Akses", type="password")
    if st.button("Masuk Sistem"):
        if token_input in VALID_TOKENS:
            st.session_state.logged_in_user = token_input
            st.session_state.user_name = VALID_TOKENS[token_input]
            if token_input not in st.session_state.user_logs:
                st.session_state.user_logs[token_input] = []
            st.rerun()
        else:
            st.error("Token salah!")
    st.stop()

current_user = st.session_state.logged_in_user
user_name = st.session_state.user_name
today_str = datetime.now().strftime("%Y-%m-%d")
user_today_clicks = [log for log in st.session_state.user_logs[current_user] if log == today_str]
sisa_kuota = MAX_DAILY_GENERATE - len(user_today_clicks)

# 3. INTERFAS UTAMA (PROSES INPUT GAMBAR MULTIMODAL)
st.title("Buat Konten Campaign. Satu Klik.")
st.write(f"Selamat bekerja, **{user_name}**. Sisa generate harian: **{sisa_kuota}/{MAX_DAILY_GENERATE}**")

st.markdown("---")

st.subheader("📦 Product Anchor (Wajib)")
product_file = st.file_uploader("Upload Foto Produk Utama", type=["jpg", "png", "jpeg"], key="prod")

col1, col2 = st.columns(2)
with col1:
    st.subheader("👤 Model (Opsional)")
    model_file = st.file_uploader("Upload Foto Model", type=["jpg", "png", "jpeg"], key="mod")
with col2:
    st.subheader("🖼️ Background (Opsional)")
    bg_file = st.file_uploader("Upload Foto Background", type=["jpg", "png", "jpeg"], key="bg")

st.markdown("---")

st.subheader("📝 Deskripsi Kampanye & Manfaat Produk")
campaign_desc = st.text_area("", placeholder="Tulis info tambahan produk di sini...")

tone = st.selectbox("GAYA BAHASA (TONE)", ["Heboh & Energetic", "Santai & Edukatif", "Formal & Profesional", "Aesthetic & Emosional"])
durasi = st.selectbox("TARGET DURASI VIDEO", [
    "15-20 Detik (Gabungan 4 Klip x 4-5 Detik)",
    "25-30 Detik (Gabungan 6 Klip x 4-5 Detik)",
    "50-60 Detik (Gabungan 12 Klip x 4-5 Detik)"
])
target_platform = st.selectbox("TARGET PLATFORM", ["TikTok & Reels (Rekomendasi)", "YouTube Shorts"])

st.markdown("""
<style>
    div.stButton > button:first-child {
        background-color: #000000; color: white; font-size: 18px; font-weight: bold; border-radius: 30px; padding: 12px 0px; border: none;
    }
</style>
""", unsafe_allow_html=True)

if st.button("✨ Generate Campaign", use_container_width=True):
    if len(user_today_clicks) >= MAX_DAILY_GENERATE:
        st.error("Kuota harian Anda habis!")
    elif not product_file:
        st.error("Anda wajib mengunggah foto 'Product Anchor' agar AI bisa menganalisis wujud fisik produk!")
    else:
        with st.spinner("Mengidentifikasi visual produk dan merancang prompt..."):
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                
                # Arsitektur Prompt Dapur Rahasia Bertingkat (Multimodal)
                system_instruction = """Kamu adalah AI Copywriter Eksekutif dan Ahli Strategi Iklan Video Pendek Konversi Tinggi. 
Tugas utamanya adalah membaca detail visual gambar 'Product Anchor' (dan gambar opsional model/background jika disediakan), lalu menggabungkannya dengan teks deskripsi dari pengguna.

Hasilkan naskah iklan terstruktur berbasis durasi kelipatan klip 4-5 detik.
Setiap adegan WAJIB memiliki format:
1. Scene [Nomor]: [Durasi Detik]
2. Visual Prompt (Bahasa Inggris detail untuk Leonardo AI): Tulis deskripsi visual yang sangat spesifik yang MEMPERTAHANKAN detail bentuk, warna, dan jenis produk dari gambar Product Anchor yang diberikan agar konsisten. Jangan biarkan produk berubah bentuk di AI generator video.
3. Narasi/Voiceover (Bahasa Indonesia): Teks persuasif lisan yang sesuai dengan TONE pilihan pengguna."""

                model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
                
                # Menyusun paket data konten (Gambar + Teks) untuk dikirim ke Gemini
                content_payload = []
                
                # Membuka file gambar ke format PIL Image agar dipahami Gemini
                prod_img = Image.open(product_file)
                content_payload.append("Ini adalah gambar utama produk (Product Anchor) yang wajib dianalisis secara presisi: ")
                content_payload.append(prod_img)
                
                if model_file:
                    mod_img = Image.open(model_file)
                    content_payload.append("Ini adalah referensi visual model/talent tambahan: ")
                    content_payload.append(mod_img)
                    
                if bg_file:
                    bg_img = Image.open(bg_file)
                    content_payload.append("Ini adalah referensi visual latar belakang/background yang diinginkan: ")
                    content_payload.append(bg_img)
                
                # Menambahkan parameter teks
                user_text_prompt = f"\nInstruksi Tambahan Pengguna:\nDeskripsi Kampanye: {campaign_desc}\nTone Bahasa: {tone}\nPilihan Durasi: {durasi}\nPlatform: {target_platform}"
                content_payload.append(user_text_prompt)
                
                # Kirim paket gabungan foto + teks ke Google Gemini
                response = model.generate_content(content_payload)
                
                st.session_state.user_logs[current_user].append(today_str)
                st.success("Analisis Visual & Konten Sukses Dibuat!")
                st.markdown("### 📋 Hasil Rencana Alur Video Berbasis Visual Produk")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Gagal memproses gambar. Pastikan format file benar. Eror: {str(e)}")
