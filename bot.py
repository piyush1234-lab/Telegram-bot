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
CHANNEL_ID = "@underage_editz"
ADMIN_ID = 6803356420
DELIVERY_BOT_USERNAME = "Coder_using_ai_bot"

sessions = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Posting bot is running.\n\nUse /post to create a post."
    )

# ================= POST =================

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    sessions[update.effective_user.id] = {}
    await update.message.reply_text("📸 Send the image.")

# ================= IMAGE =================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in sessions:
        return

    sessions[uid]["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("✍️ Send the caption text.")

# ================= TEXT HANDLER =================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in sessions:
        return

    s = sessions[uid]

    if "caption" not in s:
        s["caption"] = update.message.text
        await ask_layout(update)
        return

    if s.get("awaiting") == "file1":
        s["file1"] = update.message.text
        if s["layout"] == 2:
            s["awaiting"] = "link1"
            await update.message.reply_text(
                "🔗 Send INSTAGRAM link (for INSTAGRAM button)."
            )
        else:
            s["awaiting"] = "file2"
            await update.message.reply_text(
                "📦 Send CODE project key (for CODE button)."
            )
        return

    if s.get("awaiting") == "file2":
        s["file2"] = update.message.text
        s["awaiting"] = "link1"
        await update.message.reply_text(
            "🔗 Send INSTAGRAM link (for INSTAGRAM button)."
        )
        return

    if s.get("awaiting") == "link1":
        s["link1"] = update.message.text
        if s["layout"] in (2, 3):
            await show_preview(update)
        else:
            s["awaiting"] = "link2"
            await update.message.reply_text(
                "🔗 Send WEBSITE link (for WEBSITE button)."
            )
        return

    if s.get("awaiting") == "link2":
        s["link2"] = update.message.text
        await show_preview(update)

# ================= ASK LAYOUT =================

async def ask_layout(update: Update):
    keyboard = [
        [InlineKeyboardButton("2 Buttons", callback_data="layout_2")],
        [InlineKeyboardButton("3 Buttons", callback_data="layout_3")],
        [InlineKeyboardButton("4 Buttons", callback_data="layout_4")]
    ]
    await update.message.reply_text(
        "🔘 Choose button layout:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= LAYOUT CALLBACK (FIXED) =================

async def layout_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    layout = int(query.data.split("_")[1])
    sessions[uid]["layout"] = layout
    sessions[uid]["awaiting"] = "file1"

    if layout == 2:
        await query.message.reply_text(
            "📦 Send CODE project key (for CODE button)."
        )
    else:
        await query.message.reply_text(
            "📦 Send APK project key (for APK button)."
        )

# ================= PREVIEW =================

async def show_preview(update: Update):
    uid = update.effective_user.id
    s = sessions[uid]

    if s["layout"] == 2:
        buttons = [[
            InlineKeyboardButton(
                "CODE",
                url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={s['file1']}"
            ),
            InlineKeyboardButton("INSTAGRAM", url=s["link1"])
        ]]

    elif s["layout"] == 3:
        buttons = [
            [
                InlineKeyboardButton(
                    "APK",
                    url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={s['file1']}"
                ),
                InlineKeyboardButton(
                    "CODE",
                    url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={s['file2']}"
                )
            ],
            [
                InlineKeyboardButton("INSTAGRAM", url=s["link1"])
            ]
        ]

    else:  # layout 4
        buttons = [
            [
                InlineKeyboardButton(
                    "APK",
                    url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={s['file1']}"
                ),
                InlineKeyboardButton(
                    "CODE",
                    url=f"https://t.me/{DELIVERY_BOT_USERNAME}?start={s['file2']}"
                )
            ],
            [
                InlineKeyboardButton("INSTAGRAM", url=s["link1"]),
                InlineKeyboardButton("WEBSITE", url=s["link2"])
            ]
        ]

    markup = InlineKeyboardMarkup(buttons)
    s["final_buttons"] = markup

    await update.message.reply_photo(
        photo=s["photo"],
        caption="🔍 **PREVIEW**\n\n" + s["caption"],
        reply_markup=markup,
        parse_mode="Markdown"
    )

    confirm = [
        [
            InlineKeyboardButton("✅ POST", callback_data="confirm"),
            InlineKeyboardButton("❌ CANCEL", callback_data="cancel")
        ]
    ]

    await update.message.reply_text(
        "Confirm post?",
        reply_markup=InlineKeyboardMarkup(confirm)
    )

# ================= CONFIRM =================

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()

    s = sessions.get(uid)
    if not s or "final_buttons" not in s:
        await query.message.reply_text("⚠️ Session expired. Please /post again.")
        sessions.pop(uid, None)
        return

    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=s["photo"],
        caption=s["caption"],
        reply_markup=s["final_buttons"]
    )

    sessions.pop(uid)
    await query.message.reply_text("✅ Posted to channel.")

# ================= CANCEL =================

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.callback_query.from_user.id
    sessions.pop(uid, None)
    await update.callback_query.message.reply_text("❌ Cancelled.")

# ================= INIT =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(layout_choice, pattern="^layout_"))
    app.add_handler(CallbackQueryHandler(confirm, pattern="^confirm$"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel$"))

    app.run_polling()

if __name__ == "__main__":
    main()