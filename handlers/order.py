# from telebot import types

# # Simple in-memory per-user state. For a long-running bot you may want to persist this.
# user_data = {}

# def order_callback(call, bot):
#     try:
#         bot.answer_callback_query(call.id)
#     except Exception:
#         pass

#     user_id = str(call.from_user.id)
#     if user_id not in user_data:
#         user_data[user_id] = {}

#     if call.data == "order_checkout":
#         markup = types.InlineKeyboardMarkup()
#         markup.row(types.InlineKeyboardButton("🪑 Dine-in", callback_data="order_dinein"))
#         markup.row(types.InlineKeyboardButton("🏠 Delivery", callback_data="order_delivery"))
#         bot.edit_message_text("🚚 Choose delivery method:", call.message.chat.id, call.message.message_id, reply_markup=markup)

#     elif call.data in ["order_dinein", "order_delivery"]:
#         user_data[user_id]["order_type"] = "Dine-in" if call.data == "order_dinein" else "Delivery"
#         bot.edit_message_text("Please send your *name* to continue.", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
#         user_data[user_id]["awaiting"] = "name"

# def collect_user_data(message, bot):
#     user_id = str(message.from_user.id)
#     if user_id not in user_data or "awaiting" not in user_data[user_id] or not user_data[user_id]["awaiting"]:
#         return

#     key = user_data[user_id]["awaiting"]
#     value = message.text
#     user_data[user_id][key] = value

#     if key == "name":
#         if user_data[user_id].get("order_type") == "Dine-in":
#             bot.send_message(message.chat.id, "Enter your *table number*:", parse_mode="Markdown")
#             user_data[user_id]["awaiting"] = "table"
#         else:
#             bot.send_message(message.chat.id, "Enter your *delivery address*:", parse_mode="Markdown")
#             user_data[user_id]["awaiting"] = "address"
#         return

#     if key in ["table", "address"]:
#         user_data[user_id]["awaiting"] = None
#         bot.send_message(message.chat.id, f"✅ Order confirmed!\nType: {user_data[user_id].get('order_type')}\nName: {user_data[user_id].get('name')}")


import os
import json
from telebot import types
from datetime import datetime
from handlers import menu
from handlers.menu import user_carts, save_order

# Simple in-memory per-user order state
user_data = {}

def order_callback(call, bot):
    """Handles delivery method selection and user input prompts."""
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    user_id = str(call.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = {}

    # --- Step 1: User clicks checkout ---
    if call.data == "order_checkout":
        cart = user_carts.get(call.from_user.id, [])
        if not cart:
            bot.answer_callback_query(call.id, "🛒 Your cart is empty!")
            return

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🪑 Dine-in", callback_data="order_dinein"),
            types.InlineKeyboardButton("🏠 Delivery", callback_data="order_delivery")
        )

        bot.edit_message_text(
            "🚚 *Choose delivery method:*",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    # --- Step 2: User chooses dine-in or delivery ---
    elif call.data in ["order_dinein", "order_delivery"]:
        user_data[user_id]["order_type"] = "Dine-in" if call.data == "order_dinein" else "Delivery"
        bot.edit_message_text(
            "Please send your *name* to continue.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        user_data[user_id]["awaiting"] = "name"


def collect_user_data(message, bot):
    """Sequentially collects user details (name, table or address)."""
    user_id = str(message.from_user.id)
    if user_id not in user_data or "awaiting" not in user_data[user_id]:
        return

    key = user_data[user_id]["awaiting"]
    value = message.text.strip()
    user_data[user_id][key] = value

    # --- Step 3: Collect name ---
    if key == "name":
        if user_data[user_id].get("order_type") == "Dine-in":
            bot.send_message(message.chat.id, "Enter your *table number*:", parse_mode="Markdown")
            user_data[user_id]["awaiting"] = "table"
        else:
            bot.send_message(message.chat.id, "Enter your *delivery address*:", parse_mode="Markdown")
            user_data[user_id]["awaiting"] = "address"
        return

    # --- Step 4: Collect table number or address and finalize ---
    if key in ["table", "address"]:
        user_data[user_id]["awaiting"] = None

        cart = user_carts.get(int(user_id), [])

        # Helper: parse price from item, remove dollar sign if present and convert to float
        def _item_price(it):
            # it may be a dict like {'name':..., 'price': ' $10.99'} or a string/number
            if isinstance(it, dict):
                raw = it.get('price', 0)
            else:
                raw = it
            try:
                s = str(raw).replace('$', '').replace(',', '').strip()
                return float(s)
            except Exception:
                return 0.0

        # we'll compute total below from menu data and quantities
        total = 0.0

        order_summary = (
            f"✅ *Order Confirmed!*\n\n"
            f"👤 Name: {user_data[user_id].get('name')}\n"
            f"🏷 Type: {user_data[user_id].get('order_type')}\n"
        )

        if key == "table":
            order_summary += f"🪑 Table: {user_data[user_id].get('table')}\n"
        else:
            order_summary += f"📍 Address: {user_data[user_id].get('address')}\n"

        order_summary += "\n🍽 *Items:*\n"

        # load menu data once
        menu_data = menu.load_menu()

        total = 0.0
        for item_name, quantity in cart.items():
            item_data = next((i for i in menu_data if i.get('name') == item_name), None)
            if item_data:
                raw_price = item_data.get('price', 0)
                try:
                    price_val = float(str(raw_price).replace('$', '').replace(',', '').strip())
                except Exception:
                    price_val = 0.0
                subtotal = price_val * int(quantity)
                total += subtotal
                order_summary += f"- {item_name} x{quantity} (${subtotal:.2f})\n"
            else:
                order_summary += f"- {item_name} x{quantity}\n"

        order_summary += f"\n💰 *Total:* ${total:.2f}\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        bot.send_message(message.chat.id, order_summary, parse_mode="Markdown")

        # --- Save the order ---
        save_order(int(user_id))

        # Clear temporary data
        user_data[user_id] = {}
        
        # Thank the user and provide payment instructions + Back to Menu button
        account = os.getenv("PAYMENT_ACCOUNT", "Account: 0123456789")
        thank_text = (
            "Thank you! 🎉 Your order has been received.\n"
            f"Please make payment to the following account:\n{account}\n\n"
            "After payment, please send a photo of the payment receipt here to confirm your order."
        )
        menu_button = types.InlineKeyboardMarkup()
        menu_button.add(types.InlineKeyboardButton("🍽️ Back to Menu", callback_data="menu_show"))
        bot.send_message(message.chat.id, thank_text, parse_mode="Markdown", reply_markup=menu_button)

        # Send/forward order details to admin (if ADMIN_CHAT_ID is set)
        admin_id = os.getenv("ADMIN_CHAT_ID")
        if admin_id:
            try:
                admin_chat = int(admin_id)
                admin_text = (
                    f"📥 New order from {user_data[user_id].get('name')} (id: {user_id})\n"
                    f"Type: {user_data[user_id].get('order_type')}\n"
                    f"Items and totals:\n{order_summary}\n"
                    f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                bot.send_message(admin_chat, admin_text, parse_mode="Markdown")
            except Exception as e:
                print(f"Failed to send order to admin: {e}")
