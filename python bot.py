import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

os.makedirs("downloads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Send a video first\n"
        "Then choose:\n"
        "/480p /720p /1080p"
    )

# SAVE VIDEO
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    file_path = f"downloads/{update.message.video.file_id}.mp4"
    await file.download_to_drive(file_path)

    context.user_data["video"] = file_path
    await update.message.reply_text("✅ Video saved! Now choose resolution.")

# CHANGE RESOLUTION
def change_resolution(input_file, output_file, resolution):
    os.system(f"ffmpeg -i {input_file} -vf scale=-2:{resolution} {output_file}")

# PROCESS
async def process_resolution(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "video" not in context.user_data:
        await update.message.reply_text("❌ Send video first")
        return

    res = update.message.text.replace("/", "")
    input_file = context.user_data["video"]
    output_file = f"outputs/output_{res}.mp4"

    await update.message.reply_text("⏳ Processing...")

    change_resolution(input_file, output_file, res)

    if not os.path.exists(output_file):
        await update.message.reply_text("❌ Error processing video")
        return

    with open(output_file, "rb") as vid:
        await update.message.reply_video(vid)

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["480p", "720p", "1080p"], process_resolution))
app.add_handler(MessageHandler(filters.VIDEO, save_video))

app.run_polling()
