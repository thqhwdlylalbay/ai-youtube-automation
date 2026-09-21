import streamlit as st
import asyncio
import edge_tts
from huggingface_hub import InferenceClient
from PIL import Image
import tempfile
import os
from gradio_client import Client, handle_file

# إعدادات الصفحة والاتجاه من اليمين للشمال (RTL)
st.set_page_config(page_title="استوديو الذكاء الاصطناعي", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
        }
        .stButton>button {
            width: 100%;
            background-color: #2E7D32;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 استوديو الذكاء الاصطناعي المجاني")
st.write("تطبيق متعدد الخدمات: توليد صور، تحويل النصوص لأصوات عربية حقيقية، وتحريك الصور.")

tab1, tab2, tab3 = st.tabs(["🖼️ توليد الصور", "🗣️ أصوات عربية واقعية", "🎬 تحريك الصور"])

# ------------------- Tab 1: توليد الصور -------------------
with tab1:
    st.header("توليد الصور (Flux.1 Schnell)")
    hf_token = st.text_input("أدخل مفتاح Hugging Face المجاني (HF Token):", type="password")
    prompt = st.text_area("وصف الصورة (يفضل باللغة الإنجليزية لأفضل نتيجة):", "A highly detailed cinematic photo of an ancient castle in a desert at sunset, 8k resolution")

    if st.button("توليد الصورة الآن"):
        if not hf_token:
            st.error("يرجى إدخال مفتاح Hugging Face أولاً (يمكنك الحصول عليه مجاناً من huggingface.co).")
        else:
            with st.spinner("جاري إنشاء الصورة..."):
                try:
                    client = InferenceClient("black-forest-labs/FLUX.1-schnell", token=hf_token)
                    image = client.text_to_image(prompt)
                    st.image(image, caption="الصورة الناتجة", use_container_width=True)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التوليد: {e}")

# ------------------- Tab 2: الأصوات العربية -------------------
with tab2:
    st.header("توليد أصوات عربية طبيعية (Microsoft Neural)")
    text_input = st.text_area("أدخل النص العربي المراد تحويله إلى صوت:", "مرحباً بك! هذا صوت عربي واقعي جداً يتم إنشاؤه عبر الذكاء الاصطناعي مجاناً.")

    voices = {
        "سلمى - مصري (أنثى)": "ar-EG-SalmaNeural",
        "شاكر - مصري (ذكر)": "ar-EG-ShakirNeural",
        "حامد - سعودي (ذكر)": "ar-SA-HamedNeural",
        "زارينا - إماراتي (أنثى)": "ar-AE-ZariyahNeural"
    }

    selected_voice_name = st.selectbox("اختر المعلق الصوتي:", list(voices.keys()))
    selected_voice = voices[selected_voice_name]

    if st.button("إنشاء الملف الصوتي"):
        if not text_input.strip():
            st.error("يرجى كتابة نص أولاً.")
        else:
            with st.spinner("جاري معالجة الصوت..."):
                async def generate_audio():
                    communicate = edge_tts.Communicate(text_input, selected_voice)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                        await communicate.save(tmp_file.name)
                        return tmp_file.name

                try:
                    audio_path = asyncio.run(generate_audio())
                    st.audio(audio_path, format="audio/mp3")
                    with open(audio_path, "rb") as f:
                        st.download_button("تحميل الصوت MP3", data=f, file_name="arabic_speech.mp3", mime="audio/mp3")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء توليد الصوت: {e}")

# ------------------- Tab 3: تحريك الصور -------------------
with tab3:
    st.header("تحريك الصور (Image to Video)")
    uploaded_file = st.file_uploader("اختر صورة من جهازك لتحريكها:", type=["png", "jpg", "jpeg"])

    if uploaded_file and st.button("تحريك الصورة الآن"):
        with st.spinner("جاري تحريك الصورة عبر سيرفرات الذكاء الاصطناعي (قد يستغرق دقيقة)..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    tmp_img.write(uploaded_file.getvalue())
                    tmp_img_path = tmp_img.name

                # استخدام API مجاني لتحريك الصور (Stable Video Diffusion)
                client = Client("stabilityai/stable-video-diffusion")
                result = client.predict(
                    handle_file(tmp_img_path),
                    0,       # Seed
                    False,   # Randomize seed
                    api_name="/video"
                )
                st.video(result)
            except Exception as e:
                st.error(f"السيرفر المجاني مشغول حالياً أو حدث خطأ. التفاصيل: {e}")
