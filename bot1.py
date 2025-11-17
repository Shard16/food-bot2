import telebot
from telebot import types
import sqlite3
import os
from datetime import datetime

BOT_TOKEN = '7761763367:AAG3FYnS8EJmb7BBxMJklEudNGmnbewnA5E'
bot = telebot.TeleBot(BOT_TOKEN)

DB_FILE = 'bot_database.db'
user_info = {}

# ============================================================
# DATABASE SETUP
# ============================================================

def connect_db():
    return sqlite3.connect(DB_FILE, timeout=10)

def create_tables():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                ticket_number TEXT PRIMARY KEY,
                client_chat_id INTEGER,
                manager_chat_id INTEGER,
                order_status TEXT DEFAULT 'pending',
                paid BOOLEAN DEFAULT FALSE,
                restaurant TEXT,
                name TEXT,
                phone TEXT,
                address TEXT,
                delivery_mode TEXT
            )
        """)
        conn.commit()

create_tables()

# ============================================================
# RESTAURANT DATA
# ============================================================

restaurants = [
    "🍔 Five Guys", "🌯 Chipotle", "🍕 Pizza",
    "🍜 Panda Express", "🍗 Wingstop", "🥩 Texas Road House",
    "🍦 Dairy Queen", "🌮 Qdoba", "🍔 Sonic Drive"
]

restaurant_data = {
    "🍚 Jollof Rice": {"photo": "Jollof.png", "text": "🍚 45% OFF\n🍚 $40 Min Cart\n🍚 Pickup & Delivery"},
    "🍚 Fried Rice": {"photo": "fried.png", "text": "🍚 50% OFF\n🍚 $40 Min total cart\n🍚 Delivery & Pickup"},
    "🍕 Pizza": {"photo": "Pizza.png", "text": "🍕 50% OFF\n🍕 $40 Min total cart\n🍕 Delivery & Pickup"},
    "🍔 Hamburger": {"photo": "Ham.png", "text": "🍔 50% OFF\n🍔 $40 Min cart\n🍔 Delivery & Pickup"},
    "🍗 Wings": {"photo": "wings.png", "text": "🍗 50% OFF\n🍗 $45 Min cart\n🍗 Delivery & Pickup"},
    "🍾 Soft Drinks": {"photo": "Soft.jpeg", "text": "🍾 45% OFF\n🍾 $40 Min cart\n🍾 Pickup Only"},
    # "🍦 Dairy Queen": {"photo": "DQ.jpeg", "text": "🍦 50% OFF\n🍦 $40 Min cart\n🍦 Pickup & Delivery"},
    # "🌮 Qdoba": {"photo": "Qdoba.jpeg", "text": "🌮 50% OFF\n🌮 $40 Min cart\n🌮 Pickup only"},
    # "🍔 Sonic Drive": {"photo": "Sonic.jpeg", "text": "🍔 60% OFF\n🍔 $40 Min cart\n🍔 Pickup & Delivery"}
}

# ============================================================
# HELPERS
# ============================================================

def generate_order_number():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(CAST(ticket_number AS INTEGER)) FROM orders")
        max_num = cursor.fetchone()[0]
        return str(int(max_num) + 1 if max_num else 1)

def save_order_to_db(details):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (ticket_number, client_chat_id, restaurant, name, phone, address, delivery_mode, order_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            ON CONFLICT(ticket_number) DO UPDATE SET
                client_chat_id = excluded.client_chat_id,
                restaurant = excluded.restaurant,
                name = excluded.name,
                phone = excluded.phone,
                address = excluded.address,
                delivery_mode = excluded.delivery_mode,
                order_status = 'pending'
        """, (
            details['order_number'], details['client_chat_id'], details['restaurant'],
            details['name'], details['phone'], details['address'], details['delivery_mode']
        ))
        conn.commit()

def mark_order_as_paid(ticket_number):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET paid = TRUE WHERE ticket_number = ?", (ticket_number,))
        conn.commit()

# ============================================================
# COMMAND HANDLERS
# ============================================================

@bot.message_handler(commands=['start', 'order'])
def start(message):
    try:
        with open('Logo.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo=photo, caption="🍴 Welcome to Chef Restaurants!🍴")

        markup = types.InlineKeyboardMarkup(row_width=2)
        for r in restaurant_data.keys():
            markup.add(types.InlineKeyboardButton(r, callback_data=r))
        bot.send_message(message.chat.id, "Please choose a Meal:", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error loading menu: {e}")

# ============================================================
# RESTAURANT SELECTION
# ============================================================



@bot.callback_query_handler(func=lambda call: call.data in restaurant_data.keys())
def handle_restaurant_selection(call):
    
    try:
        data = restaurant_data[call.data]
        with open(data['photo'], 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo=photo, caption=data['text'])
        bot.send_message(call.message.chat.id, "Please enter your name:")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, get_name)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error: {e}")

def get_name(message):
    user_id = str(message.from_user.id)
    user_info[user_id]['name'] = message.text
    bot.send_message(message.chat.id, "Enter your phone number:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_phone)

def get_phone(message):
    user_id = message.from_user.id
    user_info[user_id]['phone'] = message.text
    bot.send_message(message.chat.id, "Enter your full delivery address:")
    bot.register_next_step_handler_by_chat_id(message.chat.id, get_address)

def get_address(message):
    user_id = message.from_user.id
    user_info[user_id]['address'] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Pickup", callback_data="pickup"),
        types.InlineKeyboardButton("Delivery", callback_data="delivery")
    )
    bot.send_message(message.chat.id, "Select delivery mode:", reply_markup=markup)

# ============================================================
# DELIVERY MODE
# ============================================================

@bot.callback_query_handler(func=lambda call: call.data in ["pickup", "delivery"])
def delivery_mode_selected(call):
    user_id = call.from_user.id
    user_info[user_id]['delivery_mode'] = call.data
    info = user_info[user_id]

    summary = (
        f"📦 Order Summary:\n"
        f"Order #: {info['order_number']}\n"
        f"Restaurant: {info['restaurant']}\n"
        f"Name: {info['name']}\n"
        f"Phone: {info['phone']}\n"
        f"Address: {info['address']}\n"
        f"Delivery Mode: {info['delivery_mode'].capitalize()}\n"
    )
    bot.send_message(call.message.chat.id, summary)

    save_order_to_db(info)
    notify_managers(info)
    bot.answer_callback_query(call.id, f"{call.data.capitalize()} mode selected!")

# ============================================================
# MANAGER NOTIFICATION
# ============================================================

def notify_managers(order):
    manager_group_chat_id = -5039394194  # Change this to your Telegram group ID
    order_message = (
        f"🆕 New Order #{order['order_number']}\n"
        f"🍴 {order['restaurant']}\n"
        f"👤 {order['name']}\n"
        f"📞 {order['phone']}\n"
        f"📍 {order['address']}\n"
        f"🚚 {order['delivery_mode'].capitalize()}\n"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Accept Order", callback_data=f"accept_{order['order_number']}"),
        types.InlineKeyboardButton("Mark Paid", callback_data=f"paid_{order['order_number']}")
    )
    bot.send_message(manager_group_chat_id, order_message, reply_markup=markup)

# ============================================================
# CALLBACKS
# ============================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith('paid_'))
def mark_paid(call):
    ticket_number = call.data.split('_')[1]
    mark_order_as_paid(ticket_number)
    bot.answer_callback_query(call.id, f"✅ Order #{ticket_number} marked as paid!")

# ============================================================
# MAIN LOOP
# ============================================================

print("🤖 Bot is running...")
bot.infinity_polling()
