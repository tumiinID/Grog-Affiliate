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
                
                # System Instruction yang diperketat agar menghasilkan pemisah yang konsisten
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
                
                # LOGIKA PINTAR: Memecah teks per scene dan menyisipkan gambar asli lewat kode Python st.image
                raw_text = response.text
                scenes = raw_text.split("---")
                
                for scene in scenes:
                    if scene.strip():
                        # Tampilkan teks naskah scene terlebih dahulu
                        st.markdown(scene)
                        
                        # Cari kata kunci gambar di dalam teks scene untuk dijadikan gambar nyata
                        if "- Image_Keywords:" in scene:
                            try:
                                keywords = scene.split("- Image_Keywords:")[1].strip().split("\n")[0].strip()
                                # Bersihkan karakter aneh jika ada
                                keywords = keywords.replace("[", "").replace("]", "")
                                
                                # Buat URL Pollinations resmi secara otomatis
                                image_url = f"https://image.pollinations.ai/p/{keywords}?width=600&height=350&seed=42"
                                
                                # Paksa tampilkan sebagai gambar asli di aplikasi Streamlit!
                                st.image(image_url, caption="💡 Rekomendasi Visual Scene", use_container_width=True)
                                st.markdown("<br>", unsafe_allow_html=True)
                            except:
                                pass
                
            except Exception as e:
                st.error(f"Gagal memproses. Eror: {str(e)}")
