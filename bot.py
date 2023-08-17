import telebot
import config
from main import run_parser
from selenium import webdriver

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
    data_from_parser = run_parser()
    if isinstance(data_from_parser, str):
        bot.send_message(message.chat.id, data_from_parser)
    else:
        #for i in data_from_parser:
        bot.send_message(message.chat.id, data_from_parser) #f"Title: {i['Title']}\nSalary: {i['Salary']}")


if __name__ == '__main__':
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    options = webdriver.ChromeOptions()
    options.add_argument(f'--headers="{headers}"')
    options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    bot.polling(none_stop=True)

