import streamlit as st
import requests
import asyncio
import edge_tts
import tempfile
import os
from PIL import Image
from gradio_client import Client, handle_file

# إعدادات الصفحة الرئيسية
st.set_page_config(page_title="استوديو الذكاء الاصطناعي الشامل", page_icon="🎨", layout="centered")

st.title("🎨 استوديو الذكاء الاصطناعي المصري")
st.write("تطبيق متكامل: توليد صور، تحويل النص إلى أصوات مصرية (أب، أم، أطفال)، وتحريك الصور إلى فيديو.")

# إنشاء التبويبات
tab1, tab2, tab3 = st.tabs(["🖼️ توليد الصور (Flux)", "🗣️ أصوات مصرية واقعية", "🎬 تحريك الصور"])

# ------------------- Tab 1: توليد الصور -------------------
with tab1:
    st.header("توليد الصور عالية الدقة (Flux.1 Schnell)")
    
    hf_token = st.text_input("أدخل مفتاح Hugging Face المجاني (HF Token):", type="password", help="احصل عليه مجاناً من موقع Hugging Face -> Settings -> Access Tokens")
    prompt = st.text_area("وصف الصورة (يفضل باللغة الإنجليزية للحصول على أفضل نتيجة):", value="A highly detailed cinematic photo of an ancient castle in a desert at sunset, 8k resolution")
    
    if st.button("توليد الصورة الآن", key="gen_img_btn"):
        if not hf_token:
            st.warning("يرجى إدخال مفتاح Hugging Face أولاً.")
        elif not prompt:
            st.warning("يرجى كتابة وصف للتقاط الصورة.")
        else:
            with st.spinner("جاري رسم الصورة، يرجى الانتظار..."):
                try:
                    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
                    
                    if response.status_code == 200:
                        image_bytes = response.content
                        st.image(image_bytes, caption="الصورة الناتجة", use_column_width=True)
                    else:
                        st.error(f"حدث خطأ في السيرفر: {response.status_code}. تأكد من صحة المفتاح.")
                except Exception as e:
                    st.error(f"خطأ أثناء الاتصال: {e}")

# ------------------- Tab 2: الأصوات المصرية -------------------
with tab2:
    st.header("تحويل النص إلى صوت مصري بواقعية عالية")
    
    text_input = st.text_area("اكتب النص المراد تحويله لصوت مصري:", value="أهلاً بكم في تطبيقنا الجديد! نتمنى أن تنال هذه الخدمة إعجابكم.")
    
    # اختيار شخصية الصوت المصري
    voice_option = st.selectbox(
        "اختر الصوت المصري المطلوب:",
        [
            "أم / امرأة مصرية (سلمى)",
            "أب / رجل مصري (شاكر)",
            "طفلة صغيرة مصرية",
            "طفل صغير مصري"
        ]
    )
    
    # تحديد إعدادات الصوت بناءً على الخيار
    if voice_option == "أم / امرأة مصرية (سلمى)":
        voice_id = "ar-EG-SalmaNeural"
        pitch = "+0Hz"
        rate = "+0%"
    elif voice_option == "أب / رجل مصري (شاكر)":
        voice_id = "ar-EG-ShakirNeural"
        pitch = "+0Hz"
        rate = "+0%"
    elif voice_option == "طفلة صغيرة مصرية":
        voice_id = "ar-EG-SalmaNeural"
        pitch = "+22Hz"  # رفع النبرة لتصبح كصوت طفلة
        rate = "+12%"   # تسريع بسيط يلائم أسلوب الأطفال
    elif voice_option == "طفل صغير مصري":
        voice_id = "ar-EG-ShakirNeural"
        pitch = "+28Hz"  # رفع النبرة لتصبح كصوت طفل
        rate = "+12%"

    async def generate_audio(text, voice, pitch, rate, output_file):
        communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
        await communicate.save(output_file)

    if st.button("إنشاء الصوت الآن", key="gen_audio_btn"):
        if not text_input.strip():
            st.warning("يرجى كتابة نص أولاً.")
        else:
            with st.spinner("جاري إنشاء الملف الصوتي المصري..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                        output_path = tmp_audio.name

                    asyncio.run(generate_audio(text_input, voice_id, pitch, rate, output_path))
                    
                    st.audio(output_path, format="audio/mp3")
                    st.success("تم توليد الصوت بنجاح!")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء إنشاء الصوت: {e}")

# ------------------- Tab 3: تحريك الصور -------------------
with tab3:
    st.header("تحريك الصور (Image to Video)")
    st.info("قم برفع صورة واحدة فقط بصيغة PNG أو JPG لتحريكها.")
    
    uploaded_file = st.file_uploader("اختر صورة من جهازك:", type=["png", "jpg", "jpeg"], accept_multiple_files=False, key="single_img_uploader")

    if uploaded_file is not None:
        image_preview = Image.open(uploaded_file)
        st.image(image_preview, caption="الصورة المرفوعة", width=350)
        
        if st.button("🎬 ابدأ تحريك الصورة الآن", key="anim_btn"):
            with st.spinner("جاري تحريك الصورة وتحويلها لفيديو... قد يستغرق ذلك دقيقة:"):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                        tmp_img.write(uploaded_file.getvalue())
                        tmp_img_path = tmp_img.name

                    # الاتصال بمحرك التحريك
                    client = Client("stabilityai/stable-video-diffusion")
                    result = client.predict(
                        handle_file(tmp_img_path),
                        0,       # Seed
                        False,   # Randomize seed
                        api_name="/video"
                    )
                    st.video(result)
                    st.success("تم تحريك الصورة بنجاح!")
                except Exception as e:
                    st.error(f"السيرفر المجاني للتحريك مشغول حالياً، يرجى المحاولة مرة أخرى بعد قليل. التفاصيل: {e}")
