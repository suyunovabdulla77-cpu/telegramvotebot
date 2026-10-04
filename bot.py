import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKENINGIZNI_SHU_YERGA")
CHANNEL = os.getenv("CHANNEL_USERNAME", "@KANAL_USERNAME")

# Ovoz berish variantlari
OPTIONS = [
    ("65-DMTT", "65"),
    ("36-DMTT", "36"),
    ("52-DMTT", "52"),
    ("17-DMTT", "17"),
    ("1-DMTT", "1"),
    ("56-DMTT", "56"),
]

db = sqlite3.connect("votes.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS votes (
    user_id INTEGER PRIMARY KEY,
    option TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS counts (
    option TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0
)
""")

for name, key in OPTIONS:
    cur.execute(
        "INSERT OR IGNORE INTO counts(option, count) VALUES (?, 0)",
        (key,)
    )
db.commit()


def is_member_status(status):
    return status in ("member", "administrator", "creator")


async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return is_member_status(member.status)
    except Exception:
        return False


def vote_keyboard():
    buttons = []
    for name, key in OPTIONS:
        cur.execute("SELECT count FROM counts WHERE option=?", (key,))
        count = cur.fetchone()[0]
        buttons.append([
            InlineKeyboardButton(
                f"{name} | {count}",
                callback_data=f"vote:{key}"
            )
        ])
    return InlineKeyboardMarkup(buttons)


def join_keyboard():
    channel_name = CHANNEL.lstrip("@")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📢 Kanalga a’zo bo‘lish",
            url=f"https://t.me/{channel_name}"
        )],
        [InlineKeyboardButton(
            "✅ A’zo bo‘ldim",
            callback_data="check"
        )]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_member(context.bot, user_id):
        await update.message.reply_text(
            "🗳 Ovoz berish uchun avval kanalimizga a’zo bo‘ling.",
            reply_markup=join_keyboard()
        )
        return

    await update.message.reply_text(
        "👇 Ovoz bermoqchi bo‘lgan variantingizni tanlang:",
        reply_markup=vote_keyboard()
    )


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "check":
        if not await is_member(context.bot, user_id):
            await query.answer(
                "❌ Siz hali kanalga a’zo bo‘lmagansiz.",
                show_alert=True
            )
            return

        await query.answer("✅ A’zoligingiz tasdiqlandi!")
        await query.edit_message_text(
            "👇 Ovoz bermoqchi bo‘lgan variantingizni tanlang:",
            reply_markup=vote_keyboard()
        )
        return

    if query.data.startswith("vote:"):
        if not await is_member(context.bot, user_id):
            await query.answer(
                "❌ Avval kanalga a’zo bo‘ling.",
                show_alert=True
            )
            return

        cur.execute("SELECT option FROM votes WHERE user_id=?", (user_id,))
        if cur.fetchone():
            await query.answer(
                "⚠️ Siz allaqachon ovoz bergansiz!",
                show_alert=True
            )
            return

        option = query.data.split(":", 1)[1]

        valid_keys = {key for _, key in OPTIONS}
        if option not in valid_keys:
            await query.answer("Noto‘g‘ri variant.", show_alert=True)
            return

        cur.execute(
            "INSERT INTO votes(user_id, option) VALUES (?, ?)",
            (user_id, option)
        )
        cur.execute(
            "UPDATE counts SET count=count+1 WHERE option=?",
            (option,)
        )
        db.commit()

        await query.edit_message_reply_markup(
            reply_markup=vote_keyboard()
        )
        await query.answer("✅ Ovozingiz qabul qilindi!", show_alert=True)


def main():
    if TOKEN == "BOT_TOKENINGIZNI_SHU_YERGA":
        raise RuntimeError("BOT_TOKEN muhit o‘zgaruvchisini kiriting.")
    if CHANNEL == "@KANAL_USERNAME":
        raise RuntimeError("CHANNEL_USERNAME muhit o‘zgaruvchisini kiriting.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback))
    app.run_polling()


if __name__ == "__main__":
    main()
