import telebot
import random
import time
import threading
from telebot import types

# আপনার দেওয়া টোকেন
API_TOKEN = '8633159426:AAH2S1PB3z-TaxjetcCATLmxXsauLd2P1oY'
bot = telebot.TeleBot(API_TOKEN)

# ডেটাবেজ (সাময়িকভাবে ডিকশনারি ব্যবহার করা হচ্ছে)
enabled_groups = set()
auto_reaction_status = {} # {group_id: True/False}
broadcast_messages = {} # {group_id: "message"}
last_reaction_time = {} # একই মেসেজে বারবার রিয়াকশন রোধ করতে

REACTIONS = ["👍", "❤️", "🔥", "🥰", "👏", "⚡️", "🤩", "😎"]

# /start কমান্ড
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    start_button = types.InlineKeyboardButton("Start Bot 🚀", callback_data="main_menu")
    markup.add(start_button)
    bot.send_message(message.chat.id, "স্বাগতম! বটটি সেটআপ করতে নিচের বাটনে ক্লিক করুন।", reply_markup=markup)

# মেইন মেনু (Start এ চাপ দেওয়ার পর)
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def main_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Auto Reaction ⚡️", callback_data="reaction_menu")
    btn2 = types.InlineKeyboardButton("Auto Broadcast 📢", callback_data="broadcast_menu")
    markup.add(btn1, btn2)
    bot.edit_message_text("নিচের অপশন থেকে একটি সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# /set কমান্ড - গ্রুপে কাজ করার জন্য
@bot.message_handler(commands=['set'])
def set_group(message):
    if message.chat.type == 'group' or message.chat.type == 'supergroup':
        enabled_groups.add(message.chat.id)
        bot.reply_to(message, "✅ এই গ্রুপটি বটের কাজের জন্য সেট করা হয়েছে!")
    else:
        bot.reply_to(message, "এটি কেবল গ্রুপে ব্যবহার করুন।")

# রিয়াকশন মেনু
@bot.callback_query_handler(func=lambda call: call.data == "reaction_menu")
def reaction_menu(call):
    markup = types.InlineKeyboardMarkup()
    on = types.InlineKeyboardButton("On ✅", callback_data="react_on")
    off = types.InlineKeyboardButton("Off ❌", callback_data="react_off")
    markup.add(on, off)
    bot.edit_message_text("Auto Reaction কন্ট্রোল করুন:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("react_"))
def toggle_reaction(call):
    status = True if call.data == "react_on" else False
    auto_reaction_status[call.message.chat.id] = status
    bot.answer_callback_query(call.id, f"Auto Reaction {'চালু' if status else 'বন্ধ'} হয়েছে।")

# ব্রডকাস্ট মেনু
@bot.callback_query_handler(func=lambda call: call.data == "broadcast_menu")
def broadcast_menu(call):
    markup = types.InlineKeyboardMarkup()
    on = types.InlineKeyboardButton("On Broadway (Broadcast) 📢", callback_data="broad_on")
    markup.add(on)
    bot.edit_message_text("ব্রডকাস্ট সেটআপ করতে নিচের বাটনে চাপ দিন:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "broad_on")
def ask_broadcast_msg(call):
    msg = bot.send_message(call.message.chat.id, "Type your message: (আপনি যা লিখবেন তা ১০ মিনিট পর পর গ্রুপে যাবে)")
    bot.register_next_step_handler(msg, save_broadcast_msg)

def save_broadcast_msg(message):
    broadcast_messages[message.chat.id] = message.text
    bot.send_message(message.chat.id, "✅ ব্রডকাস্ট মেসেজ সেভ হয়েছে! ১০ মিনিট পর পর এটি গ্রুপে পাঠানো হবে।")

# ১০ মিনিট পর পর ব্রডকাস্ট পাঠানোর ফাংশন
def broadcast_loop():
    while True:
        time.sleep(600) # ৬০০ সেকেন্ড = ১০ মিনিট
        for group_id in list(enabled_groups):
            if group_id in broadcast_messages:
                try:
                    bot.send_message(group_id, broadcast_messages[group_id])
                except:
                    pass

# গ্রুপে রিয়াকশন দেওয়ার লজিক
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    if message.chat.id in enabled_groups and auto_reaction_status.get(message.chat.id):
        # একই মেসেজে বারবার রিয়াকশন রোধ
        if message.message_id not in last_reaction_time:
            try:
                bot.set_message_reaction(message.chat.id, message.message_id, [types.ReactionTypeEmoji(random.choice(REACTIONS))])
                last_reaction_time[message.message_id] = True
            except:
                pass

# ব্রডকাস্ট থ্রেড চালু
threading.Thread(target=broadcast_loop, daemon=True).start()

print("Bot is running...")
bot.infinity_polling()
                            
