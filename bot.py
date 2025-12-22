import requests
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)



# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT")
TRUECALLER_API_KEY = os.getenv("KEY")
FORCE_CHANNEL = "@TechBotss"

# Official Truecaller SDK lookup endpoint (example)
TRUECALLER_API_URL = "https://api.truecaller.com/v1/lookup"

# ============================================


async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(update, context):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ Joined", callback_data="joined")]
        ])
        await update.message.reply_text(
            "🚫 **Bot use karne ke liye pehle channel join karo**",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "👋 **Welcome to Truecaller Lookup Bot**\n\n"
        "📞 *Number bhejo country code ke sath*\n\n"
        "Example:\n"
        "`+919876543210`",
        parse_mode="Markdown"
    )


async def lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(update, context):
        await update.message.reply_text("❌ Pehle channel join karo.")
        return

    number = update.message.text.strip()

    headers = {
        "Authorization": f"Bearer {TRUECALLER_API_KEY}",
        "Accept": "application/json",
    }

    params = {
        "phone": number,
        "countryCode": "IN"  # optional, API ke hisaab se
    }

    try:
        r = requests.get(TRUECALLER_API_URL, headers=headers, params=params, timeout=10)

        if r.status_code != 200:
            await update.message.reply_text("⚠️ Lookup failed. Invalid number or API issue.")
            return

        data = r.json()

        # ---- Adjust keys based on your API response ----
        name = data.get("name", "Unknown")
        tag = data.get("type", "Unknown")
        spam = data.get("spamScore", "N/A")
        country = data.get("country", "Unknown")
        carrier = data.get("carrier", "Unknown")

        text = (
            "📞 **Truecaller Lookup Result**\n\n"
            f"👤 **Name:** {name}\n"
            f"🏷 **Tag:** {tag}\n"
            f"⚠️ **Spam Score:** {spam}\n"
            f"📡 **Carrier:** {carrier}\n"
            f"🌍 **Country:** {country}\n\n"
            "⚡ _Powered by Truecaller_"
        )

        await update.message.reply_text(text, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text("❌ Error occurred. Try again later.")


# ================== RUN BOT ==================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup))

print("🤖 Truecaller Bot Running...")
app.run_polling()
