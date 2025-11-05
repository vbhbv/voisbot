import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from transformers import AutoProcessor, SpeechT5ForTextToSpeech
import torch
import soundfile as sf

# ===== متغير البيئة =====
TOKEN = os.getenv("BOT_TOKEN")

# ===== تحميل نموذج MBZUAI/SpeechT5 عربي =====
processor = AutoProcessor.from_pretrained("MBZUAI/speecht5_tts_clartts_ar")
model = SpeechT5ForTextToSpeech.from_pretrained("MBZUAI/speecht5_tts_clartts_ar")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# ===== رسالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبًا! أنا بوت نطق النصوص بالعربية 🔊\n"
        "أرسل لي أي نص وسأحوّله إلى صوت.\n"
        "يمكنك اختيار الصوت بين رجل وامرأة لاحقًا."
    )

# ===== تحويل النص إلى صوت =====
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ أرسل نصًا لتحويله إلى صوت.")
        return

    await update.message.reply_text("⏳ جاري توليد الصوت...")

    # تجهيز الإدخال
    inputs = processor(text=text, return_tensors="pt").to(device)
    
    # توليد الصوت
    with torch.no_grad():
        speech = model.generate_speech(inputs["input_ids"], speaker=0)  # speaker=0 للذكر، 1 للأنثى

    # حفظ الملف
    out_file = "output.wav"
    sf.write(out_file, speech.cpu().numpy(), samplerate=16000)

    # إرسال الملف
    await update.message.reply_audio(audio=open(out_file, "rb"), filename="speech.wav")
    os.remove(out_file)

# ===== التشغيل =====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))
    print("🚀 بوت نطق النصوص جاهز للعمل")
    app.run_polling()

if __name__ == "__main__":
    main()
