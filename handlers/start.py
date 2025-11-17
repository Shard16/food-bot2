from telebot import types

def start(message, bot):
    try:
        with open('Logo.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo=photo, caption="🍴 Welcome to Chef Restaurants!🍴")
        buttons = [
            [types.InlineKeyboardButton("🍽️ View Menu", callback_data="menu_show")],
            # [types.InlineKeyboardButton("🛒 View Cart", callback_data="cart_view")],
            [types.InlineKeyboardButton("📞 Contact", url="https://t.me/mrireolde")]
        ]
        markup = types.InlineKeyboardMarkup()
        for row in buttons:
            markup.row(*row)

        bot.send_message(
            message.chat.id,
            "👋 Welcome to Tasty Delights! Ready to order something delicious?",
            parse_mode="Markdown",
            reply_markup=markup
    )
    except Exception as e:
        bot.send_message(message.chat.id, f"Error loading menu: {e}")
        
    
        
