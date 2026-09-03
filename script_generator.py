import os
import google.generativeai as genai

# إعداد مفتاح الـ Gemini API (سنجعله يأخذ المفتاح من إعدادات الأمان لاحقاً، أو تضدعي مفتاحك للتجربة)
# يفضل وضع مفتاحك هنا مؤقتاً للتجربة، أو عبر Environment Variables
API_KEY = "AQ.Ab8RN6LMWP6ASM7ybU_nzWcklkmjT6FOtr50juJ9MqjVWEy2_w"

genai.configure(api_key=API_KEY)

def generate_youtube_content(niche_topic):
    # استخدام أحدث وأقوى نموذج لتوليد المحتوى الإبداعي
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    You are an expert YouTube content creator and scriptwriter for a top-tier US-based channel focusing on: {niche_topic}.
    Your target audience is US viewers interested in AI, making money online, and future technology.
    
    Please generate:
    1. A catchy, high-CTR YouTube title (optimized for US audience).
    2. A complete, engaging 15-minute video script outline and main script in English, starting with a powerful hook in the first 3 seconds, broken down into clear sections.
    3. Optimized YouTube description with tags and keywords.
    
    Topic focus for this generation: How AI and smart automation are creating new millionaires in 2026, and a step-by-step blueprint anyone can follow.
    """
    
    print(f"Generating content for US audience on topic: {niche_topic}...")
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    topic = "AI, Money, and Future Technology Automation"
    script_output = generate_youtube_content(topic)
    
    # حفظ النتيجة في ملف نصي محلياً
    with open("generated_script.txt", "w", encoding="utf-8") as f:
        f.write(script_output)
        
    print("Done! Script generated successfully and saved to generated_script.txt")
