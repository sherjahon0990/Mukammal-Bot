# KODNI TO‘LIQ YANGILANGAN HOLDA BERAMAN

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import logging
import requests

# Token
TOKEN = '8024891367:AAE7eWHb-BpVixqwotbeRwfNM7WMLQYXzSs'
bot = telebot.TeleBot(TOKEN)

# Admin ID
ADMIN_ID = 7114973309

# Majburiy obuna kanallar ro'yxati
forced_channels = set()

# Foydalanuvchilar va chatlar
chat_to_user = {}
user_to_chat = {}
active_users = set()

logging.basicConfig(level=logging.INFO)

def delete_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    response = requests.get(url)
    if response.ok:
        print("✅ Webhook muvaffaqiyatli o‘chirildi.")
    else:
        print("❌ Webhookni o‘chirishda xato:", response.text)

def check_subscription(user_id):
    for channel in forced_channels:
        url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            status = data["result"]["status"]
            if status not in ["member", "creator", "administrator"]:
                return False
        else:
            return False
    return True

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    active_users.add(chat_id)

    if not check_subscription(chat_id):
        markup = InlineKeyboardMarkup()
        for ch in forced_channels:
            markup.add(InlineKeyboardButton(f"🔗 {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
        bot.send_message(chat_id, "📢 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=markup)
        return

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Chatni boshlash"))
    bot.send_message(chat_id, "Salom! Quyidagi tugmani bosing:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if check_subscription(call.message.chat.id):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("Chatni boshlash"))
      
        bot.send_message(call.message.chat.id, "✅ Obuna tasdiqlandi. Endi foydalanishingiz mumkin.", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❗ Hali hamma kanallarga obuna bo‘lmagansiz.")

@bot.message_handler(commands=['admin'])
def admin_admin(message):
    if message.chat.id != ADMIN_ID:
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📊 Statistika"), KeyboardButton("🔧 Kanal sozlamalari"))
    markup.add(KeyboardButton("⬅️ Orqaga"))
    bot.send_message(message.chat.id, "🛠 Admin paneliga xush kelibsiz:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "📊 Statistika")
def show_stats(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, f"""📊 *Statistika:*
👥 Foydalanuvchilar soni: {len(active_users)}
💬 Chat bog‘langanlar (admin → user): {len(chat_to_user)}
🔁 Chat bog‘langanlar (user → admin): {len(user_to_chat)}
Majburiy obuna kanallari: {', '.join(forced_channels) if forced_channels else 'Yo‘q'}
""", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🔧 Kanal sozlamalari")
def kanal_sozlamalari(message):
    if message.chat.id != ADMIN_ID:
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("➕ Kanal qo‘shish"), KeyboardButton("➖ Kanal o‘chirish"))
    markup.add(KeyboardButton("⬅️ Orqaga"))
    bot.send_message(message.chat.id, "Kanal sozlamalarini tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "➕ Kanal qo‘shish")
def add_channel(message):
    msg = bot.send_message(message.chat.id, "🆕 Kanal `@username` ko‘rinishida yuboring:")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(message):
    if not message.text.startswith('@'):
        bot.send_message(message.chat.id, "❗ Noto‘g‘ri format. Iltimos, `@kanal_username` ko‘rinishida yuboring.")
        return
    forced_channels.add(message.text.strip())
    bot.send_message(message.chat.id, f"✅ {message.text} kanali majburiy obunaga qo‘shildi.")

@bot.message_handler(func=lambda msg: msg.text == "➖ Kanal o‘chirish")
def remove_channel(message):
    msg = bot.send_message(message.chat.id, "❌ O‘chirmoqchi bo‘lgan kanal `@username`ini yuboring:")
    bot.register_next_step_handler(msg, delete_channel)

def delete_channel(message):
    username = message.text.strip()
    if username in forced_channels:
        forced_channels.remove(username)
        bot.send_message(message.chat.id, f"✅ {username} kanali majburiy obunadan o‘chirildi.")
    else:
        bot.send_message(message.chat.id, "❌ Bunday kanal majburiy obunada mavjud emas.")

@bot.message_handler(func=lambda msg: msg.text == "⬅️ Orqaga")
def back_to_admin(message):
    admin_admin(message)

@bot.message_handler(func=lambda message: message.text == "Chatni boshlash")
def ask_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Foydalanuvchining ID raqamini kiriting:", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(message, register_chat)

def register_chat(message):
    chat_id = message.chat.id
    user = message.text.strip()

    try:
        user_id = int(user)
    except ValueError:
        bot.send_message(chat_id, "❗ Faqat raqam kiriting.")
        bot.register_next_step_handler(message, register_chat)
        return

    try:
        bot.send_message(user_id, "👋 Sizga admin tomonidan xabar yuborilmoqda.")
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        bot.send_message(chat_id, "❗ Bu foydalanuvchi hali botga /start yubormagan.")
        return

    chat_to_user[chat_id] = user_id
    user_to_chat[user_id] = chat_id

    bot.send_message(chat_id, "✅ Endi xabar yuborishingiz mumkin.")

@bot.message_handler(content_types=["text", "photo", "video", "voice", "document", "audio", "video_note", "sticker"])
def handle_all_messages(message):
    chat_id = message.chat.id
    user = chat_to_user.get(chat_id)
    original_chat_id = user_to_chat.get(chat_id)

    if original_chat_id:
        receiver = original_chat_id
    elif user:
        receiver = user
    else:
        if message.chat.id == ADMIN_ID:
            return
        bot.send_message(chat_id, "❗ Avval 'Chatni boshlash' tugmasini bosing.")
        return

    try:
        if message.content_type == "text":
            bot.send_message(receiver, message.text)
        elif message.content_type == "photo":
            bot.send_photo(receiver, message.photo[-1].file_id, caption=message.caption)
        elif message.content_type == "video":
            bot.send_video(receiver, message.video.file_id, caption=message.caption)
        elif message.content_type == "voice":
            bot.send_voice(receiver, message.voice.file_id)
        elif message.content_type == "audio":
            bot.send_audio(receiver, message.audio.file_id, caption=message.caption)
        elif message.content_type == "document":
            bot.send_document(receiver, message.document.file_id, caption=message.caption)
        elif message.content_type == "video_note":
            bot.send_video_note(receiver, message.video_note.file_id)
        elif message.content_type == "sticker":
            bot.send_sticker(receiver, message.sticker.file_id)
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        bot.send_message(chat_id, "❗ Xabar yuborilmadi.")

if __name__ == "__main__":
    delete_webhook()
    print("🤖 Bot ishga tushdi...")
    bot.polling(none_stop=True)

