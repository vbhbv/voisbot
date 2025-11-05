import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ===== مكتبات TTS =====
from transformers import AutoProcessor, SpeechT5ForTextToSpeech
import torch
from scipy.io.wavfile import write
import soundfile as sf

# ===== إعداد النموذج =====
MODEL_PATH = "models/speecht5_tts_clartts_ar"

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = SpeechT5ForTextToSpeech.from_pretrained(MODEL_PATH)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# ===== رسالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت نطق النصوص بالعربية 🔊\n"
        "أرسل أي نص بالعربية وسأحوله لك إلى صوت بجودة عالية.\n"
        "يمكنك اختيار الصوت: رجل أو امرأة باستخدام كلمات: 'صوت رجل' أو 'صوت امرأة' في بداية النص."
    )

# ===== دالة التحويل إلى صوت =====
def text_to_speech(text, voice="female", file_path="output.wav"):
    # إعداد نبرة الصوت
    speaker = "alloy" if voice=="male" else "aria"

    # توليد الموجة الصوتية
    inputs = processor(text=text, return_tensors="pt")
    speech = model.generate_speech(**inputs, speaker=speaker, sample_rate=24000)

    # حفظ الصوت
    sf.write(file_path, speech.cpu().numpy(), 24000)
    return file_path

# ===== التعامل مع الرسائل =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # تحديد الصوت
    voice = "female"
    if text.lower().startswith("صوت رجل"):
        voice = "male"
        text = text[8:].strip()
    elif text.lower().startswith("صوت امرأة"):
        voice = "female"
        text = text[10:].strip()

    if not text:
        await update.message.reply_text("⚠️ أرسل نصًا لتحويله إلى صوت.")
        return

    await update.message.reply_text("⏳ جاري تحويل النص إلى صوت...")

    file_path = f"tts_output_{update.message.message_id}.wav"
    await asyncio.to_thread(text_to_speech, text, voice, file_path)

    # إرسال الصوت
    await update.message.reply_audio(audio=open(file_path, "rb"), caption="✅ تم تحويل النص إلى صوت!")
    os.remove(file_path)

# ===== التشغيل =====
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 بوت نطق النصوص يعمل الآن!")
    app.run_polling()

if __name__ == "__main__":
    main()
