import telebot
import config
#from main import lst_telegram

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('static/sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!, \nЯ - <b>{1.first_name}</b>, короче говоря бот.'.format(message.from_user, bot.get_me()),
    parse_mode='html')


@bot.message_handler(content_types=['text'])
def lalala(message):
    bot.send_message(message.chat.id, message.text)
    #bot.send_message(message.chat.id, message.from_user.is_bot)
    # for i in lst_telegram:
    #     bot.send_message(i['Title'], i['Salary'])

if __name__ == '__main__':
    bot.polling(none_stop=True)

