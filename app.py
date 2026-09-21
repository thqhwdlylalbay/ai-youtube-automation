import streamlit as st
import requests
import asyncio
import edge_tts
import tempfile
import os
import time
from PIL import Image
from gradio_client import Client, handle_file
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips

# إعدادات الصفحة
st.set_page_config(page_title="استوديو السينما بالذكاء الاصطناعي", page_icon="🎬", layout="centered")

st.title("🎬 استوديو السينما والمشاهد المتكامل")
st.write("اصنع مشهداً كاملاً: حرك الصورة، ولّد حوار الشخصيات بأصوات مصرية، وادمج الصوت مع الفيديو تلقائياً!")

# التبويبات
tab1, tab2, tab3 = st.tabs(["🖼️ توليد الصور", "🗣️ الأصوات المصرية", "🎬 صانع المشاهد الناطقة (فيديو + صوت)"])

# ------------------- Tab 1: توليد الصور -------------------
with tab1:
    st.header("توليد صور ومشاهد واقعية")
    hf_token = st.text_input("مفتاح Hugging Face المجاني (HF Token):", type="password")
    prompt_ar = st.text_area("وصف المشهد بالعربي:", value="صورة سينمائية واقعية جداً لعائلة وروبوت يجلسون على طاولة الطعام بدقة 8k")
    
    if st.button("توليد الصورة", key="gen_img"):
        if not hf_token:
            st.warning("أدخل مفتاح Hugging Face أولاً.")
        else:
            with st.spinner("جاري الرسم..."):
                try:
                    translated = GoogleTranslator(source='auto', target='en').translate(prompt_ar)
                    res = requests.post(
                        "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
                        headers={"Authorization": f"Bearer {hf_token}"},
                        json={"inputs": translated}
                    )
                    if res.status_code == 200:
                        st.image(res.content, caption="الصورة الناتجة", use_column_width=True)
                    else:
                        st.error("تأكد من صحة المفتاح أو انتظر ثوانٍ.")
                except Exception as e:
                    st.error(f"خطأ: {e}")

# ------------------- Tab 2: الأصوات المنفصلة -------------------
with tab2:
    st.header("توليد صوت مصري منفصل")
    text = st.text_area("النص المراد تحويله لصوت:", value="أهلاً بكم في بيتنا الجديد!")
    voice_choice = st.selectbox("اختر الصوت:", ["أم / امرأة مصرية", "أب / رجل مصري", "طفلة صغيرة", "طفل صغير", "روبوت مصري"])
    
    if st.button("إنشاء الصوت", key="single_voice"):
        with st.spinner("جاري إنشاء الصوت..."):
            voice_id = "ar-EG-SalmaNeural" if "امرأة" in voice_choice or "طفلة" in voice_choice else "ar-EG-ShakirNeural"
            p_val = "+25Hz" if "طفل" in voice_choice or "روبوت" in voice_choice else "+0Hz"
            r_val = "+15%" if "روبوت" in voice_choice else "+0%"
            
            async def make_speech():
                comm = edge_tts.Communicate(text, voice_id, pitch=p_val, rate=r_val)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    await comm.save(tmp.name)
                    return tmp.name
            
            aud_path = asyncio.run(make_speech())
            st.audio(aud_path)

# ------------------- Tab 3: المونتاج التلقائي للمشهد الكامل -------------------
with tab3:
    st.header("🎬 إنشاء مشهد سينمائي متكامل (حركة + أصوات)")
    st.info("ارفع صورة المشهد واكتب حوار الشخصيات، وسيقوم التطبيق بتحريك الصورة ودمج الحوار معها فوراً!")
    
    uploaded_img = st.file_uploader("ارفع صورة المشهد (روبوت، عائلة، إلخ):", type=["png", "jpg", "jpeg", "webp"], key="cinematic_img")
    
    st.subheader("📝 سيناريو وحوار المشهد:")
    robot_text = st.text_input("كلام الروبوت (اختياري):", value="جاهز لخدمتكم يا فندم!")
    mom_text = st.text_input("كلام الأم (اختياري):", value="تسلم إيدك يا روبوت، الأكل ممتاز!")
    kid_text = st.text_input("كلام الطفل/الطفلة (اختياري):", value="أنا بحب الروبوت ده أوي!")
    
    if uploaded_img and st.button("🚀 ابدأ إنتاج المشهد الكامل الآن"):
        temp_audio_path = None
        
        # 1. إنشاء الحوار الصوتي
        with st.spinner("1/3: جاري توليد حوار الشخصيات بالمصرية..."):
            try:
                audio_clips = []
                
                async def gen_clip(txt, v_id, pitch="+0Hz", rate="+0%"):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                        comm = edge_tts.Communicate(txt, v_id, pitch=pitch, rate=rate)
                        await comm.save(f.name)
                        return f.name

                if robot_text.strip():
                    f1 = asyncio.run(gen_clip(robot_text, "ar-EG-ShakirNeural", pitch="+30Hz", rate="+10%"))
                    audio_clips.append(AudioFileClip(f1))
                if mom_text.strip():
                    f2 = asyncio.run(gen_clip(mom_text, "ar-EG-SalmaNeural", pitch="+0Hz", rate="+0%"))
                    audio_clips.append(AudioFileClip(f2))
                if kid_text.strip():
                    f3 = asyncio.run(gen_clip(kid_text, "ar-EG-SalmaNeural", pitch="+25Hz", rate="+10%"))
                    audio_clips.append(AudioFileClip(f3))

                if audio_clips:
                    final_audio = concatenate_audioclips(audio_clips)
                    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    temp_audio_path = temp_audio.name
                    final_audio.write_audiofile(temp_audio_path, logger=None)
                    st.success("تم تجهيز الحوار الصوتي بنجاح!")
                    st.audio(temp_audio_path)
            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الصوت: {e}")

        # 2. تحريك الصورة عبر سيرفر الفيديو مع محاولة إعادة الاتصال
        vid_path = None
        with st.spinner("2/3: جاري الاتصال بسيرفر تحريك الصورة... (قد يستغرق دقيقة)"):
            try:
                img = Image.open(uploaded_img).convert('RGB')
                img.thumbnail((1024, 1024))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_i:
                    img.save(tmp_i.name, format="PNG")
                    img_path = tmp_i.name

                client = Client("stabilityai/stable-video-diffusion")
                result = client.predict(handle_file(img_path), 0, False, api_name="/video")
                
                vid_path = result[0] if isinstance(result, (list, tuple)) else result
            except Exception as e:
                st.warning("السيرفر المجاني مشغول جداً حالياً بطلبات إضافية. جاري محاولة ثانية...")
                time.sleep(3)
                try:
                    client = Client("stabilityai/stable-video-diffusion")
                    result = client.predict(handle_file(img_path), 0, False, api_name="/video")
                    vid_path = result[0] if isinstance(result, (list, tuple)) else result
                except Exception as e2:
                    st.error("السيرفر المجاني للتحريك مزدحم في هذه اللحظة. اضغط على الزر مرة أخرى بعد القليل من الوقت.")

        # 3. الدمج النهائي للملفين
        if vid_path:
            with st.spinner("3/3: جاري دمج حركة المشهد مع الحوار الصوتي..."):
                try:
                    video_clip = VideoFileClip(vid_path)
                    
                    if temp_audio_path:
                        audio_clip = AudioFileClip(temp_audio_path)
                        if audio_clip.duration > video_clip.duration:
                            video_clip = video_clip.loop(duration=audio_clip.duration)
                        else:
                            video_clip = video_clip.subclip(0, audio_clip.duration)
                            
                        final_video = video_clip.set_audio(audio_clip)
                    else:
                        final_video = video_clip

                    output_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                    final_video.write_videofile(output_final, codec="libx264", audio_codec="aac", logger=None)
                    
                    st.success("🎉 تم إنتاج المشهد السينمائي الناطق بنجاح!")
                    st.video(output_final)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الدمج النهائي: {e}")
