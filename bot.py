import os
from dotenv import load_dotenv
import telebot
from telebot import types
from database import init_db

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_ACCOUNT = os.getenv("PAYMENT_ACCOUNT")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

from handlers import start, menu, cart, order

bot = telebot.TeleBot(BOT_TOKEN)


# Message / command handlers
@bot.message_handler(commands=["start"])
def _handle_start(message):
    start.start(message, bot)


# Callback handlers
@bot.callback_query_handler(func=lambda call: call.data == "menu_show")
def _handle_menu(call):
    menu.menu_callback(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def handle_add_to_cart(call):
    menu.add_to_cart(call, bot)


# @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("cart_"))
# def _handle_cart(call):
#     cart.cart_callback(call, bot)

@bot.callback_query_handler(func=lambda call: call.data == "cart_view")
def handle_view_cart(call):
    cart.view_cart(call, bot)

@bot.callback_query_handler(func=lambda call: call.data == "order_checkout")
def handle_checkout(call):
    order.order_callback(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cart_"))
def handle_cart_callbacks(call):
    if call.data == "cart_clear":
        cart.clear_cart(call, bot)
    elif call.data.startswith("cart_add_"):
        cart.add_to_cart_callback(call, bot)



@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("order_"))
def _handle_order(call):
    order.order_callback(call, bot)


# Generic text handler (for collecting user data)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def _handle_text(message):
    text = message.text.strip().lower()  # clean and lowercase text

    # Define greeting words to catch
    greetings = [
    "hi", "hello", "hey", "yo", "sup", "wassup", "how far", "howfa", "how far na",
    "how you dey", "wetin dey", "wagwan", "oya", "oya now", "my gee", "my guy",
    "bros", "boss", "chairman", "oga", "madam", "good morning", "good afternoon",
    "good evening", "good day", "morning o", "afternoon o", "evening o", "how body",
    "long time", "long time no see", "you don show", "abeg", "how your side",
    "how everything", "how tins", "how you dey now", "how far my guy", "how una dey",
    "greetings", "hi there", "hello there", "hey there", "yo bro", "yo man",
    "hey mate", "hiya", "howdy", "bonjour", "salut", "hola", "ola", "ciao",
    "namaste", "shalom", "salaam", "konnichiwa", "annyeong", "ni hao",
    "merhaba", "privet", "servus", "g’day", "hiya mate", "peace", "what’s good",
    "what’s up", "whats up", "sup bro", "sup man", "hey bro", "hey sis",
    "hello friend", "yo boss", "hi boss", "hey chief", "hello chief", "hey fam",
    "yo fam", "wag1", "wag one", "hey buddy", "hey pal", "hey dude",
    "hello there general", "hey stranger", "hey big man", "hiya love", "hiya dear",
    "how’s it going", "how’s everything", "how’s your day", "what’s happening",
    "what’s popping"]

  
    # If the user says a greeting, trigger the start function
    if any(text.startswith(greet) or greet in text for greet in greetings):
        start.start(message, bot)
        return  

    # Otherwise, handle as normal text (e.g. collecting order details)
    order.collect_user_data(message, bot)

@bot.message_handler(func=lambda message: True)
def handle_user_messages(message):
    order.collect_user_data(message, bot)

if __name__ == "__main__":
    init_db()
    print("🤖 Bot is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)




# @bot.message_handler(commands=["start"])
# def start(message):
#     userid = message.chat.id
#     username = message.chat.first_name
#     bot.send_message(userid, "Hi " + username)

# @bot.message_handler(commands=["ping"])
# def ping(message):
#     userid = message.chat.id

#     markup = types.InlineKeyboardMarkup()
#     pongbutton = types.InlineKeyboardButton("PONG!", callback_data="Pong_Data")
#     pingbutton = types.InlineKeyboardButton("PING!", callback_data="Ping_Data")

#     markup.add(pongbutton)
#     markup.add(pingbutton)

    
#     bot.send_message(userid, "Ping or pong!", reply_markup=markup)

# @bot.callback_query_handler(func=lambda call:True)
# def callback_inline(call: types.CallbackQuery):

#     userid = call.message.chat.id

#     if call.data == "Pong_Data":
#         bot.send_message(userid,"Ping!")

#     if call.data == 'Ping_Data':
#         bot.send_message(userid,"Pong!")


# bot.delete_webhook(drop_pending_updates=True)

# bot.infinity_polling(timeout=1, long_polling_timeout = 3) 