import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8721157106:AAFudCgf3l8_93ortZKgz7q1EWUknZlzl2o"

user_videos = {}

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a video 🎥")

# SAVE VIDEO
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    path = f"{update.message.from_user.id}.mp4"
    await file.download_to_drive(path)

    user_videos[update.message.from_user.id] = path

    await update.message.reply_text("Video saved ✅\nUse /480 /720 /1080")

# CHANGE RESOLUTION
def change_resolution(input_file, output_file, res):
    os.system(f"ffmpeg -i {input_file} -vf scale=-2:{res} {output_file}")

# PROCESS COMMAND
async def process_resolution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_videos:
        await update.message.reply_text("Send video first ❌")
        return

    res = update.message.text.replace("/", "")
    input_file = user_videos[user_id]
    output_file = f"output_{res}.mp4"

    await update.message.reply_text("Processing... ⏳")

    change_resolution(input_file, output_file, res)

    with open(output_file, "rb") as vid:
        await update.message.reply_video(vid)

# MAIN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler(["480", "720", "1080"], process_resolution))
app.add_handler(MessageHandler(filters.VIDEO, save_video))

app.run_polling()
