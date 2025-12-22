import requests
from random import randint

try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
except ModuleNotFoundError:
    input("There is no necessary library. Complete the command line command: PIP Install Pytelegrambotapi")

# ================== CONFIG ==================
url = "https://leakosintapi.com/"
bot_token = ""      # BotFather token
api_token = ""      # Leakosint token
CHANNEL_USERNAME = "@techbotss"   # force join channel (without link)

lang = "hi"
limit = 300
# ============================================

bot = telebot.TeleBot(bot_token)

# ================== ACCESS ==================
def user_access_test(user_id):
    return True

def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except:
        return False
# ============================================

# ================== REPORT ==================
cash_reports = {}

def generate_report(query, query_id):
    global cash_reports
    data = {
        "token": api_token,
        "request": query.split("\n")[0],
        "limit": limit,
        "lang": lang
    }

    response = requests.post(url, json=data).json()
    print(response)

    if "Error code" in response:
        print("Error:", response["Error code"])
        return None

    cash_reports[str(query_id)] = []

    for database_name in response["List"].keys():
        text = [f"<b>{database_name}</b>", ""]
        text.append(response["List"][database_name]["InfoLeak"] + "\n")

        if database_name != "No results found":
            for report_data in response["List"][database_name]["Data"]:
                for column_name in report_data.keys():
                    text.append(f"<b>{column_name}</b>: {report_data[column_name]}")
                text.append("")

        text = "\n".join(text)

        if len(text) > 3500:
            text = text[:3500] + "\n\nSome data did not fit this message"

        cash_reports[str(query_id)].append(text)

    return cash_reports[str(query_id)]
# ============================================

# ================== KEYBOARD =================
def create_inline_keyboard(query_id, page_id, count_page):
    markup = InlineKeyboardMarkup()

    if page_id < 0:
        page_id = count_page - 1
    elif page_id > count_page - 1:
        page_id = 0

    if count_page == 1:
        return markup

    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("<<", callback_data=f"/page {query_id} {page_id-1}"),
        InlineKeyboardButton(f"{page_id+1}/{count_page}", callback_data="page_list"),
        InlineKeyboardButton(">>", callback_data=f"/page {query_id} {page_id+1}")
    )
    return markup
# ============================================

# ================== START ====================
@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "🚀 Join Channel",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
            )
        )
        bot.send_message(
            message.chat.id,
            "🚫 *Access Denied*\n\n"
            "Bot use karne ke liye pehle channel join karo 👇\n\n"
            "Join ke baad `/start` dubara bhejo.",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return

    bot.reply_to(
        message,
        "👋 *Welcome!*\n\n"
        "🔍 Number / Email / Username bhejo\n"
        "📂 Main leaked databases me search karunga\n\n"
        "⚡ Fast • Powerful • Clean",
        parse_mode="Markdown"
    )
# ============================================

# ================== MESSAGE ==================
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    user_id = message.from_user.id

    if not is_user_joined(user_id):
        bot.send_message(
            message.chat.id,
            f"❌ Pehle channel join karo:\n{CHANNEL_USERNAME}"
        )
        return

    if not user_access_test(user_id):
        bot.send_message(message.chat.id, "You have no access to the bot")
        return

    if message.content_type == "text":
        query_id = randint(0, 9999999)
        report = generate_report(message.text, query_id)

        if report is None:
            bot.reply_to(message, "Bot abhi kaam nahi kar raha.")
            return

        markup = create_inline_keyboard(query_id, 0, len(report))

        try:
            bot.send_message(
                message.chat.id,
                report[0],
                parse_mode="html",
                reply_markup=markup
            )
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(
                message.chat.id,
                report[0].replace("<b>", "").replace("</b>", ""),
                reply_markup=markup
            )
# ============================================

# ================== CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    if call.data.startswith("/page "):
        query_id, page_id = call.data.split(" ")[1:]

        if query_id not in cash_reports:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="❌ Request data expired"
            )
            return

        report = cash_reports[query_id]
        markup = create_inline_keyboard(query_id, int(page_id), len(report))

        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=report[int(page_id)],
                parse_mode="html",
                reply_markup=markup
            )
        except telebot.apihelper.ApiTelegramException:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=report[int(page_id)].replace("<b>", "").replace("</b>", ""),
                reply_markup=markup
            )
# ============================================

# ================== RUN ======================
while True:
    try:
        bot.polling(none_stop=True)
    except:
        pass
# ============================================
