import streamlit as st
import google.generativeai as genai
from datetime import datetime
from PIL import Image

# 1. KONFIGURASI KEAMANAN & DATA USER (TETAP AMAN & TIDAK BERUBAH)
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

st.set_page_config(
    page_title="Grog Affiliate Studio",
    page_icon="🐸",
    layout="wide"
)

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

# 2. INTERFAS UTAMA (NAMA APLIKASI BARU)
st.title("🐸 Grog Affiliate Studio")
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

# Parameter Campaign
col_a, col_b = st.columns(2)
with col_a:
    voice_type = st.selectbox(
        "KANDIDAT PENGISI SUARA (VO)", 
        [
            "Perempuan (Sangat Direkomendasikan untuk K-Pop/Skincare)", 
            "Laki-laki (Maskulin & Tegas)", 
            "Dialog Pasangan (Interaksi Laki-laki & Perempuan)",
            "Suara AI Google Text-to-Speech Standar"
        ]
    )
    tone = st.selectbox("GAYA BAHASA (TONE)", ["Heboh & Energetic", "Santai & Edukatif", "Formal & Profesional", "Aesthetic & Emosional"])

with col_b:
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

# 3. TOMBOL GENERATE DENGAN FITUR SISTEM DISPLAY GAMBAR OTOMATIS
if st.button("✨ Generate Campaign", use_container_width=True):
    if len(user_today_clicks) >= MAX_DAILY_GENERATE:
        st.error("Kuota harian Anda habis!")
    elif not product_file:
        st.error("Anda wajib mengunggah foto 'Product Anchor' agar AI bisa menganalisis wujud fisik produk!")
    else:
        with st.spinner("Mengidentifikasi visual produk dan merancang cerita beserta gambar rekomendasi..."):
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                
                # System Instruction diperketat agar memisahkan scene dengan tanda khusus '---'
                system_instruction = f"""Kamu adalah AI Copywriter Eksekutif dari Grog Affiliate Studio. 
Tugas utamanya adalah membaca detail visual gambar 'Product Anchor' lalu menggabungkannya dengan teks deskripsi dari pengguna.

Hasilkan naskah iklan terstruktur berbasis durasi kelipatan klip 4-5 detik.
Setiap adegan WAJIB memiliki format terstruktur seperti berikut:

Scene [Nomor]: [Durasi Detik]
- Visual Prompt: [Prompt detail dalam Bahasa Inggris untuk Leonardo AI]
- Narasi/Voiceover: [Teks persuasif dalam Bahasa Indonesia sesuai VO: '{voice_type}' dan TONE: '{tone}']
- Image_Keywords: [Tulis 3-5 kata kunci inti adegan ini dalam Bahasa Inggris, pisahkan HANYA dengan tanda minus tanpa spasi, contoh: sad-person-looking-at-phone]

Berikan pembatas yang jelas antar Scene menggunakan tanda '---'."""

                model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
                
                content_payload = []
                prod_img = Image.open(product_file)
                content_payload.append("Ini adalah gambar utama produk (Product Anchor): ")
                content_payload.append(prod_img)
                
                if model_file:
                    content_payload.append("Ini adalah referensi visual model: ")
                    content_payload.append(Image.open(model_file))
                    
                if bg_file:
                    content_payload.append("Ini adalah referensi visual latar belakang: ")
                    content_payload.append(Image.open(bg_file))
                
                user_text_prompt = f"\nInstruksi Tambahan Pengguna:\nDeskripsi Kampanye: {campaign_desc}\nTarget Platform: {target_platform}"
                content_payload.append(user_text_prompt)
                
                response = model.generate_content(content_payload)
                
                st.session_state.user_logs[current_user].append(today_str)
                st.success("Analisis Sukses Dibuat!")
                st.markdown("---")
                st.markdown("### 📋 Hasil Rencana Alur Video Berbasis Visual Produk")
                
                # Membaca teks mentah dan memecahnya berdasarkan tanda '---'
                raw_text = response.text
                scenes = raw_text.split("---")
                
                for scene in scenes:
                    if scene.strip():
                        # Tampilkan teks naskah scene
                        st.markdown(scene)
                        
                        # Sistem Otomatis Mengambil Kata Kunci untuk Ditampilkan Jadi Gambar Nyata
                        if "- Image_Keywords:" in scene:
                            try:
                                keywords = scene.split("- Image_Keywords:")[1].strip().split("\n")[0].strip()
                                keywords = keywords.replace("[", "").replace("]", "")
                                
                                # Membuat link request gambar ke Pollinations AI
                                image_url = f"https://image.pollinations.ai/p/{keywords}?width=600&height=350&seed=42"
                                
                                # Menampilkan gambar secara paksa di Streamlit
                                st.image(image_url, caption="💡 Rekomendasi Visual Scene", use_container_width=True)
                                st.markdown("<br>", unsafe_allow_html=True)
                            except:
                                pass
                
            except Exception as e:
                st.error(f"Gagal memproses. Eror: {str(e)}")
