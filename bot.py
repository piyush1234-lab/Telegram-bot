import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@underage_editz"        # your channel
ADMIN_ID = 6803356420                 # your Telegram user ID
DELIVERY_BOT_USERNAME = "Coder_using_gpt_bot"  # without @

# Temporary session storage
post_sessions = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Posting bot is running.\n\n"
        "Use /post to create a new channel post."
    )

# ================= POST FLOW =================

# Step 1: start post
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    post_sessions[update.effective_user.id] = {}
    await update.message.reply_text("📸 Send the image for the post.")

# Step 2: receive image
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in post_sessions:
        return

    post_sessions[uid]["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("✍️ Send the caption text.")

# Step 3: receive caption
async def handle_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in post_sessions:
        return

    session = post_sessions[uid]

    if "caption" not in session:
        session["caption"] = update.message.text
        await update.message.reply_text(
            "🔑 Send the project key (example: bike_product)\n"
            "⚠️ Must match the key used in the delivery bot."
        )
        return

    if "key" not in session:
        session["key"] = update.message.text.strip()
        await update.message.reply_text(
            "🎬 Send the WATCH HERE link (YouTube / Instagram / etc)."
        )
        return

    # Step 4: watch link
    session["watch_link"] = update.message.text.strip()

    # Build buttons (ONE ROW)
    buttons = [
        [
            InlineKeyboardButton(
                "GET CODE",
                url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={session['key']}"
            ),
            InlineKeyboardButton(
                "WATCH HERE",
                url=session["watch_link"]
            )
        ]
    ]

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))

    app.run_polling()

if __name__ == "__main__":
    main()