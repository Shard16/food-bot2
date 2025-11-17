import json
from telebot import types
from datetime import datetime
from database import save_order_to_db
from handlers.menu import user_carts, load_menu, save_order

import json
from telebot import types
from datetime import datetime
from database import save_order_to_db
from handlers.menu import user_carts, load_menu, save_order

def view_cart(call, bot):
    """Displays the user's current cart items."""
    user_id = call.from_user.id
    cart = user_carts.get(user_id, {})

    if not cart:
        bot.answer_callback_query(call.id, "Your cart is empty!")
        return

    # Load menu to get item prices
    menu_data = load_menu()

    # Build cart message
    message = "🛒 *Your Cart:*\n\n"
    total = 0
    for idx, (item_name, quantity) in enumerate(cart.items(), 1):
        # Find the matching item in the menu to get its price
        item = next((i for i in menu_data if i.get("name") == item_name), None)
        if item:
            price = item.get("price", 0)
            subtotal = price * quantity
            total += subtotal
            message += f"{idx}. {item_name} × {quantity} — ${subtotal}\n"
        else:
            message += f"{idx}. {item_name} × {quantity}\n"

    message += f"\n💰 *Total:* ${total}"

    # Buttons
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Checkout", callback_data="order_checkout"))
    markup.add(types.InlineKeyboardButton("❌ Clear Cart", callback_data="cart_clear"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_show"))

    bot.edit_message_text(
        message,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )


def clear_cart(call, bot):
    """Clears all items from user's cart."""
    user_id = call.from_user.id
    user_carts[user_id] = {}
    bot.answer_callback_query(call.id, "Cart cleared ✅")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🍽️ View Menu", callback_data="menu_show"))
    bot.edit_message_text(
        "Your cart has been cleared.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


def checkout(call, bot):
    """Handles checkout process and saves the order."""

    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    user_id = call.from_user.id
    # username = call.from_user.username or call.from_user.first_name

    success = save_order(user_id)

    if success:
        bot.edit_message_text(
            "🎉 Your order has been placed successfully! Thank you ❤️",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.edit_message_text(
            "⚠️ There was an issue placing your order. Please try again.",
            call.message.chat.id,
            call.message.message_id
        )


def add_to_cart_callback(call, bot):
    """Handles when user selects an item from menu to add to cart."""
    user_id = call.from_user.id
    item_name = call.data.split("_", 1)[1]

    menu_items = load_menu()
    item = next((i for i in menu_items if i.get("name") == item_name), None)

    if not item:
        bot.answer_callback_query(call.id, "Item not found ❌")
        return

    # Add item to cart (dictionary format: {item_name: quantity})
    if user_id not in user_carts:
        user_carts[user_id] = {}

    user_carts[user_id][item_name] = user_carts[user_id].get(item_name, 0) + 1
    bot.answer_callback_query(call.id, f"✅ Added {item['name']} to cart!")


# def load_orders():
#     try:
#         with open("data/orders.json", "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_orders(orders):
#     with open("data/orders.json", "w") as f:
#         json.dump(orders, f, indent=2)

# def cart_callback(call, bot):
#     user_id = str(call.from_user.id)
#     orders = load_orders()
#     user_cart = orders.get(user_id, [])

#     if call.data.startswith("cart_add_"):
#         item_id = call.data.split("_")[-1]
#         user_cart.append(item_id)
#         orders[user_id] = user_cart
#         save_orders(orders)
#         try:
#             bot.answer_callback_query(call.id, "✅ Added to cart!")
#         except Exception:
#             pass
#         return

#     if call.data == "cart_view":
#         if not user_cart



#             bot.edit_message_text("🛒 Your cart is empty.", call.message.chat.id, call.message.message_id)
#             return

#         cart_text = "\n".join([f"• Item ID: {item}" for item in user_cart])
#         markup = types.InlineKeyboardMarkup()
#         markup.add(types.InlineKeyboardButton("✅ Checkout", callback_data="order_checkout"))
#         bot.edit_message_text(f"🛒 *Your Cart:*\n{cart_text}", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)


