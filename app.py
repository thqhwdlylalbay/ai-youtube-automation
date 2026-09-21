import streamlit as st
import requests
import asyncio
import edge_tts
import tempfile
import os
from PIL import Image
from gradio_client import Client, handle_file
from deep_translator import GoogleTranslator

# إعدادات الصفحة
st.set_page_config(page_title="استوديو الذكاء الاصطناعي العربي", page_icon="🎬", layout="centered")

st.title("🎬 استوديو الذكاء الاصطناعي المتكامل")
st.write("تطبيق عربي بالكامل: اكتب وصفك بالعربي لتوليد صور حقيقية، أصوات مصرية واقعية، وتحريك المشاهد لملفات فيديو.")

# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs(["🖼️ توليد الصور والمشاهد", "🗣️ الأصوات المصرية الواقعية", "🎬 تحريك الصور إلى فيديو"])

# ------------------- Tab 1: توليد الصور والمشاهد بالعربي -------------------
with tab1:
    st.header("توليد صور ومشاهد واقعية جداً")
    
    hf_token = st.text_input("مفتاح Hugging Face المجاني (HF Token):", type="password")
    
    prompt_ar = st.text_area(
        "اكتب وصف المشهد أو الصورة باللغة العربية (مثال: صورة سينمائية واقعية جداً لقلعة قديمة في الصحراء وقت غروب الشمس دقة عالية):",
        value="صورة سينمائية فائقة الواقعية لشارع مصري قديم في القاهرة وقت الغروب بدقة 8k"
    )
    
    if st.button("توليد المشهد الآن", key="gen_img_btn"):
        if not hf_token:
            st.warning("يرجى أدخل مفتاح Hugging Face الخاص بك أولاً.")
        elif not prompt_ar.strip():
            st.warning("يرجى كتابة وصف الصورة بالعربي.")
        else:
            with st.spinner("جاري ترجمة الوصف وتوليد الصورة بواقعية عالية..."):
                try:
                    # ترجمة الوصف تلقائياً للإنجليزية لضمان أعلى جودة من الذكاء الاصطناعي
                    translated_prompt = GoogleTranslator(source='auto', target='en').translate(prompt_ar)
                    
                    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    response = requests.post(API_URL, headers=headers, json={"inputs": translated_prompt})
                    
                    if response.status_code == 200:
                        image_bytes = response.content
                        st.image(image_bytes, caption=f"النتيجة لـ: {prompt_ar}", use_column_width=True)
                    else:
                        st.error(f"حدث خطأ في السيرفر ({response.status_code}). تأكد من صحة المفتاح.")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء المعالجة: {e}")

# ------------------- Tab 2: الأصوات المصرية الواقعية -------------------
with tab2:
    st.header("تحويل النص إلى صوت مصري حقيقي")
    
    text_input = st.text_area("اكتب النص المراد تحويله إلى صوت:", value="أهلاً بكم في استوديو الذكاء الاصطناعي الخاص بنا! نتمنى أن تنال هذه الخدمة إعجابكم.")
    
    voice_option = st.selectbox(
        "اختر شخصية الصوت المصري:",
        [
            "أم / امرأة مصرية (سلمى)",
            "أب / رجل مصري (شاكر)",
            "طفلة صغيرة مصرية",
            "طفل صغير مصري"
        ]
    )
    
    # ضبط خيارات الصوت
    if voice_option == "أم / امرأة مصرية (سلمى)":
        voice_id = "ar-EG-SalmaNeural"
        pitch, rate = "+0Hz", "+0%"
    elif voice_option == "أب / رجل مصري (شاكر)":
        voice_id = "ar-EG-ShakirNeural"
        pitch, rate = "+0Hz", "+0%"
    elif voice_option == "طفلة صغيرة مصرية":
        voice_id = "ar-EG-SalmaNeural"
        pitch, rate = "+22Hz", "+12%"
    elif voice_option == "طفل صغير مصري":
        voice_id = "ar-EG-ShakirNeural"
        pitch, rate = "+28Hz", "+12%"

    async def generate_audio(text, voice, pitch, rate, output_file):
        communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
        await communicate.save(output_file)

    if st.button("إنشاء الصوت الآن", key="gen_audio_btn"):
        if not text_input.strip():
            st.warning("يرجى كتابة النص أولاً.")
        else:
            with st.spinner("جاري توليد الصوت المصري..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                        output_path = tmp_audio.name

                    asyncio.run(generate_audio(text_input, voice_id, pitch, rate, output_path))
                    st.audio(output_path, format="audio/mp3")
                    st.success("تم توليد الصوت بنجاح!")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء إنشاء الصوت: {e}")

# ------------------- Tab 3: تحريك الصور والمشاهد -------------------
with tab3:
    st.header("تحريك الصور وتحويلها إلى فيديو")
    st.info("قم برفع صورة واحدة فقط من جهازك لتحريكها وتحويلها لمشهد فيديو حركي.")
    
    # دعم صيغ أكثر من بينها webp
    uploaded_file = st.file_uploader("اختر صورة من جهازك:", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=False, key="img_anim_uploader")

    if uploaded_file is not None:
        try:
            image_preview = Image.open(uploaded_file)
            st.image(image_preview, caption="الصورة المرفوعة", width=350)
            
            if st.button("🎬 تحريك المشهد الآن", key="anim_btn"):
                with st.spinner("جاري معالجة الصورة وتحريكها... قد يستغرق ذلك دقيقة:"):
                    try:
                        # تحويل صيغة الصورة وحجمها تلقائياً لتناسب نموذج التحريك دون أخطاء
                        rgb_image = image_preview.convert('RGB')
                        rgb_image.thumbnail((1024, 1024)) # تقليل الحجم المناسب لمنع تعليق السيرفر
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                            rgb_image.save(tmp_img.name, format="PNG")
                            tmp_img_path = tmp_img.name

                        client = Client("stabilityai/stable-video-diffusion")
                        result = client.predict(
                            handle_file(tmp_img_path),
                            0,
                            False,
                            api_name="/video"
                        )
                        st.video(result)
                        st.success("تم تحريك المشهد بنجاح!")
                    except Exception as e:
                        st.error(f"سيرفر تحريك الصور المجاني عليه ضغط حالياً. يرجى المحاولة مرة أخرى بعد ثوانٍ. التفاصيل: {e}")
        except Exception as e:
            st.error("الصورة المرفوعة غير صالحة أو تالفة، يرجى اختيار صورة أخرى.")
