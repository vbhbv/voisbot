import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from TTS.api import TTS

TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_FOLDER = "tts_files"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ---------- نماذج TTS عربية خفيفة ----------
# صوت امرأة عربي واضح وحديث
tts_female = TTS(model_name="tts_models/ar/sammy/tacotron2-small", progress_bar=False, gpu=False)
# صوت رجل عربي واضح وحديث
tts_male   = TTS(model_name="tts_models/ar/sammy/tacotron2-small", progress_bar=False, gpu=False)

# ---------- رسالة البداية ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت نطق النصوص بالعربية 🔊\n"
        "أرسل أي نص لأحوله إلى صوت طبيعي، ثم اختر نوع الصوت:"
    )

# ---------- تحويل النص إلى صوت ----------
def text_to_speech(text: str, voice: str, filename: str):
    tts = tts_female if voice == "female" else tts_male
    tts.tts_to_file(text=text, file_path=filename)
    return filename

# ---------- استقبال الرسائل ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ أرسل نصًا صالحًا!")
        return

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

# ---------- تشغيل البوت ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🚀 بوت نطق النصوص بالعربية جاهز للعمل!")
    app.run_polling()

if __name__ == "__main__":
    main()
