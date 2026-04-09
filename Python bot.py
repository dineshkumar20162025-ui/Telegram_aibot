import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
from deep_translator import GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")

os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send a video\n"
        "Then choose:\n"
        "/480p /720p /1080p /2160p\n"
        "or /translate"
    )

# SAVE VIDEO
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    file_path = f"downloads/{update.message.video.file_id}.mp4"
    await file.download_to_drive(file_path)

    context.user_data["video"] = file_path
    await update.message.reply_text("✅ Video saved! Choose option.")

# CHANGE RESOLUTION
def change_resolution(input_file, output_file, resolution):
    os.system(f"ffmpeg -i {input_file} -vf scale=-2:{resolution} {output_file}")

# PROCESS RESOLUTION
async def process_resolution(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "video" not in context.user_data:
        await update.message.reply_text("❌ Send video first")
        return

    res = update.message.text.replace("/", "")
    input_file = context.user_data["video"]

    if os.path.getsize(input_file) > 20 * 1024 * 1024:
        await update.message.reply_text("❌ File too large (max 20MB)")
        return

    output_file = f"outputs/output_{res}.mp4"

    await update.message.reply_text("⏳ Processing...")
    change_resolution(input_file, output_file, res)

    with open(output_file, "rb") as vid:
        await update.message.reply_video(vid)

# TRANSLATE FUNCTION
def translate_video(input_video):
    audio_file = "outputs/audio.wav"

    os.system(f"ffmpeg -i {input_video} {audio_file}")

    tamil_text = GoogleTranslator(source='auto', target='ta').translate("This is a test video")

    tts = gTTS(tamil_text, lang='ta')
    tamil_audio = "outputs/tamil.mp3"
    tts.save(tamil_audio)

    output_video = "outputs/translated.mp4"
    os.system(f"ffmpeg -i {input_video} -i {tamil_audio} -map 0:v -map 1:a -c:v copy {output_video}")

    return output_video

# TRANSLATE COMMAND
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "video" not in context.user_data:
        await update.message.reply_text("❌ Send video first")
        return

    await update.message.reply_text("⏳ Translating...")

    output = translate_video(context.user_data["video"])

    try:
        with open(output, "rb") as vid:
            await update.message.reply_video(vid)
    except Exception:
        await update.message.reply_text("❌ Error occurred")

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["480p", "720p", "1080p", "2160p"], process_resolution))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(MessageHandler(filters.VIDEO, save_video))

app.run_polling()
