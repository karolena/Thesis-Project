import telebot

bot = telebot.TeleBot('6357800099:AAH_9f1kk14c629YAbsyvAXVmSkNgfApdqU')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! Обери рік: ")


# @bot.message_handler(commands=['2021'])
# def firstyear(message):
#    markup = types.InlineKeyboardMarkup()
#    markup.add(types.InlineKeyboardButton("2021"))
#    bot.send_message(message.chat.id, "Оберіть 2021 рік", reply_markup=markup)


bot.polling(none_stop=True)
