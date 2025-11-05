import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from download_model import load_local_tts

# ربط التوكن
TOKEN = os.getenv("BOT_TOKEN")

# تحميل النموذج الصوتي المحلي
tts_female, tts_male = load_local_tts()

# رسالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك! أرسل أي نص عربي وسأقوم بتحويله لصوت واضح.\n"
        "يمكنك اختيار صوت ذكر أو أنثى."
    )

# تحويل النص إلى صوت
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ يرجى إرسال نص لتحويله إلى صوت.")
        return

    await update.message.reply_text("⏳ جاري تحويل النص إلى صوت...")

    # اختيار صوت عشوائي للعرض (يمكن تعديل اختيار صوت)
    tts = tts_female  # أو tts_male

    # حفظ الصوت كملف WAV
    output_file = f"output_{update.message.message_id}.wav"
    await asyncio.to_thread(tts.tts_to_file, text=text, file_path=output_file)

    # إرسال الملف للمستخدم
    if os.path.exists(output_file):
        await update.message.reply_audio(audio=open(output_file, "rb"), caption="✅ تم تحويل النص إلى صوت!")
        os.remove(output_file)
    else:
        await update.message.reply_text("❌ حدث خطأ أثناء تحويل النص إلى صوت.")

# التشغيل
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))

    print("🚀 بوت تحويل النصوص إلى صوت يعمل الآن!")
    app.run_polling()

if __name__ == "__main__":
    main()
