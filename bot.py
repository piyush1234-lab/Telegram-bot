import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================

TOKEN = os.environ["BOT_TOKEN"]          # must exist in Railway variables
CHANNEL_ID = "@underage_editz"           # your channel username
ADMIN_ID = 6803356420                     # <-- REPLACE with your Telegram user ID

# Temporary storage for interactive posting
post_sessions = {}

# ================= BASIC START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("GET CODE", url="https://t.me/Coder_using_gpt_bot")],
        [InlineKeyboardButton("WATCH HERE", url="https://youtube.com")]
    ]
    await update.message.reply_text(
        "Bot is running.\nUse /post to create a channel post.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= INTERACTIVE POST FLOW =================

# Step 1: start post
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    post_sessions[update.effective_user.id] = {}
    await update.message.reply_text(
        "📸 Send the image for the channel post."
    )

# Step 2: receive image
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in post_sessions:
        return

    photo = update.message.photo[-1]
    post_sessions[uid]["photo"] = photo.file_id

    await update.message.reply_text(
        "✍️ Now send the caption text (you can include emojis & hashtags)."
    )

# Step 3: receive caption + buttons
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in post_sessions:
        return

    session = post_sessions[uid]

    # First text = caption
    if "caption" not in session:
        session["caption"] = update.message.text
        await update.message.reply_text(
            "🔗 Now send buttons in this format:\n\n"
            "GET CODE|https://t.me/Coder_using_gpt_bot\n"
            "WATCH HERE|https://youtube.com"
        )
        return

    # Second text = buttons
    buttons = []
    for line in update.message.text.splitlines():
        if "|" not in line:
            continue
        text, url = line.split("|", 1)
        buttons.append([
            InlineKeyboardButton(text.strip(), url=url.strip())
        ])

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=session["photo"],
        caption=session["caption"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    del post_sessions[uid]
    await update.message.reply_text("✅ Posted to channel successfully.")

# ================= BOT INIT =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
