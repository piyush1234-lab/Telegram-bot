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
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@underage_editz"                 # your channel
ADMIN_ID = 6803356420                          # your Telegram ID
DELIVERY_BOT_USERNAME = "Coder_using_ai_bot"   # without @

post_sessions = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Posting bot is running.\n\n"
        "Use /post to create a new channel post."
    )

# ================= POST FLOW =================

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    post_sessions[update.effective_user.id] = {}
    await update.message.reply_text("📸 Send the image for the post.")

# STEP 1 — IMAGE
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in post_sessions:
        return

    post_sessions[uid]["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("✍️ Send the caption text.")

# STEP 2 — CAPTION
async def handle_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    session = post_sessions.get(uid)
    if not session:
        return

    if "caption" not in session:
        session["caption"] = update.message.text
        await update.message.reply_text("📦 Send FILE 1 project key.")
        return

    if "file1" not in session:
        session["file1"] = update.message.text.strip()
        await update.message.reply_text("📦 Send FILE 2 project key.")
        return

    if "file2" not in session:
        session["file2"] = update.message.text.strip()
        await update.message.reply_text("🔗 Send LINK 1 (Watch / Demo / etc).")
        return

    if "link1" not in session:
        session["link1"] = update.message.text.strip()
        await update.message.reply_text("🔗 Send LINK 2.")
        return

    # STEP 3 — LINK 2
    session["link2"] = update.message.text.strip()

    # BUILD BUTTONS
    buttons = [
        [
            InlineKeyboardButton(
                "GET FILE 1",
                url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={session['file1']}"
            ),
            InlineKeyboardButton(
                "GET FILE 2",
                url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={session['file2']}"
            )
        ],
        [
            InlineKeyboardButton("WATCH HERE", url=session["link1"]),
            InlineKeyboardButton("MORE INFO", url=session["link2"])
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    # PREVIEW
    await context.bot.send_photo(
        chat_id=uid,
        photo=session["photo"],
        caption="🧪 *PREVIEW*\n\n" + session["caption"],
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    confirm_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ CONFIRM POST", callback_data="confirm"),
            InlineKeyboardButton("❌ CANCEL", callback_data="cancel")
        ]
    ])

    await update.message.reply_text(
        "Do you want to post this to the channel?",
        reply_markup=confirm_keyboard
    )

# ================= CONFIRM / CANCEL =================

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    session = post_sessions.get(uid)

    await query.answer()

    if not session:
        return

    if query.data == "cancel":
        post_sessions.pop(uid, None)
        await query.message.reply_text("❌ Post cancelled.")
        return

    if query.data == "confirm":
        buttons = [
            [
                InlineKeyboardButton(
                    "GET FILE 1",
                    url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={session['file1']}"
                ),
                InlineKeyboardButton(
                    "GET FILE 2",
                    url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={session['file2']}"
                )
            ],
            [
                InlineKeyboardButton("WATCH HERE", url=session["link1"]),
                InlineKeyboardButton("MORE INFO", url=session["link2"])
            ]
        ]

        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=session["photo"],
            caption=session["caption"],
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        post_sessions.pop(uid, None)
        await query.message.reply_text("✅ Posted to channel successfully.")

# ================= INIT =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_caption))
    app.add_handler(CallbackQueryHandler(confirm_handler))

    app.run_polling()

if __name__ == "__main__":
    main()