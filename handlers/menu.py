import json
import os
from datetime import datetime
from telebot import types
import sqlite3


# Global in-memory cart store
user_carts = {}

# Load menu
def load_menu():
    try:
        menu_path = os.path.join("data", "menu.json")
        with open(menu_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: menu.json not found in data directory")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in menu.json")
        return []


def menu_callback(call, bot):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    data = load_menu()
    if not data:
        bot.edit_message_text(
            "Sorry, the menu is currently unavailable.",
            call.message.chat.id,
            call.message.message_id
        )
        return

    # markup.add(types.InlineKeyboardButton("🛒 View Cart", callback_data="cart_view"))
    # bot.edit_message_text(
    #     "🍔 *Menu*:\nSelect an item to add to cart.",
    #     call.message.chat.id,
    #     call.message.message_id,
    #     parse_mode="Markdown",
    #     reply_markup=markup
    # )


    markup = types.InlineKeyboardMarkup(row_width=1)

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    
    for item in data:
        item_name = item.get('name')
        item_price = item.get('price')
        markup.add(types.InlineKeyboardButton(
            f"🍽️ {item_name} - #{item_price}",
            callback_data=f"add_{item_name}"
        ))

    markup.add(types.InlineKeyboardButton("🛒 View Cart", callback_data="cart_view"))

    text = "🍔 *Menu:*\nTap an item to add it to your cart."
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)


def add_to_cart(call, bot):
    user_id = call.from_user.id
    item_name = call.data.split("_", 1)[1]

    user_cart = user_carts.setdefault(user_id, {})
    user_cart[item_name] = user_cart.get(item_name, 0) + 1

    total_items = sum(user_cart.values())
    bot.answer_callback_query(
        call.id,
        f"✅ Added {item_name}! ({total_items} item{'s' if total_items > 1 else ''} in cart)"
    )


# def add_to_cart(user_id, item):
#     """Adds a selected item to a user's temporary cart."""
#     if user_id not in user_carts:
#         user_carts[user_id] = []
#     user_carts[user_id].append(item)


def save_order(user_id):
    """Saves all items from a user's cart into the SQLite orders table."""
    if user_id not in user_carts or not user_carts[user_id]:
        return False  # Cart is empty

    try:
        conn = sqlite3.connect("data/orders.db")  # adjust if your db path differs
        cursor = conn.cursor()

        # Load menu to get prices
        menu_data = load_menu()
        
        # user_carts[user_id] is a dict like {"item_name": quantity, "item_name2": quantity}
        for item_name, quantity in user_carts[user_id].items():
            # Find the item in the menu to get its price
            item = next((i for i in menu_data if i.get("name") == item_name), None)
            price = item.get("price") if item else 0
            total = price * quantity  # Calculate total (price * quantity)
            
            cursor.execute("""
                INSERT INTO orders (user_id, item_name, quantity, price, total, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                item_name,
                quantity,
                price,
                total,
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

        # clear the user's cart after saving
        user_carts[user_id] = {}
        return True
    except Exception as e:
        print(f"Error saving order: {e}")
        return False


# def save_order(user_id, username):
#     """Saves user's order to JSON file with timestamp and clears their cart."""
#     if user_id not in user_carts or not user_carts[user_id]:
#         return False

#     order_data = {
#         "user_id": user_id,
#         "username": username,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "items": user_carts[user_id]
#     }

#     orders_file = os.path.join("data", "orders.json")
#     try:
#         # Load existing orders
#         if os.path.exists(orders_file):
#             with open(orders_file, "r") as f:
#                 existing_orders = json.load(f)
#         else:
#             existing_orders = []

#         existing_orders.append(order_data)

#         # Save back
#         with open(orders_file, "w") as f:
#             json.dump(existing_orders, f, indent=4)

#         # Clear user cart after saving
#         user_carts[user_id] = []
#         return True

#     except Exception as e:
#         print(f"Error saving order: {e}")
#         return False
