import telebot

TOKEN = "7761763367:AAG3FYnS8EJmb7BBxMJklEudNGmnbewnA5E"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def get_chat_id(message):
    print("Chat ID:", message.chat.id)

bot.polling()
