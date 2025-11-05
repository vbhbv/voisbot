import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from TTS.api import TTS

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = "tts_files"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ---------- نماذج TTS متعددة أصوات ----------
# نبرة امرأة
tts_female = TTS(model_name="tts_models/ar/synpaflow_arabic_female", progress_bar=False, gpu=False)
# نبرة رجل
tts_male = TTS(model_name="tts_models/ar/synpaflow_arabic_male", progress_bar=False, gpu=False)

# ---------- Start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت نطق النصوص بالعربية 🔊\n"
        "أرسل لي أي نص لتحويله إلى صوت طبيعي، ثم اختر الصوت:"
    )

# ---------- تحويل النص إلى صوت ----------
def text_to_speech(text: str, voice: str, filename: str):
    tts = tts_female if voice == "female" else tts_male
    tts.tts_to_file(text=text, file_path=filename)
    return filename

# ---------- التعامل مع الرسائل ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ أرسل نصًا صالحًا!")
        return

    # إنشاء لوحة اختيار الصوت
    keyboard = [
        [InlineKeyboardButton("👩 صوت امرأة", callback_data=f"female|{text}")],
        [InlineKeyboardButton("👨 صوت رجل", callback_data=f"male|{text}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع الصوت:", reply_markup=reply_markup)

# ---------- التعامل مع اختيار الصوت ----------
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    voice, text = query.data.split("|")
    
    filename = os.path.join(DOWNLOAD_FOLDER, f"tts_{query.from_user.id}.wav")
    await asyncio.to_thread(text_to_speech, text, voice, filename)

    if os.path.exists(filename):
        await query.message.reply_audio(audio=open(filename, "rb"), caption=f"✅ تم تحويل النص إلى صوت ({voice})!")
        os.remove(filename)
    else:
        await query.message.reply_text("❌ حدث خطأ أثناء تحويل النص!")

# ---------- التشغيل ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🚀 بوت نطق النصوص بالعربية يعمل الآن")
    app.run_polling()

if __name__ == "__main__":
    main()
