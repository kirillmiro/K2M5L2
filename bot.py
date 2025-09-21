import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """
Доступные команды:
/start - начать работу с ботом и получить приветственное сообщение.
/help - получить список доступных команд.
/show_city <city_name> - отобразить указанный город на карте.
/remember_city <city_name> - сохранить город в список избранных.
/show_my_cities - показать все сохраненные города.
""")


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split()[-1]
    path = f"city_{message.chat.id}.png"
    if manager.create_grapf(path, [city_name]):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "Такого города нет в базе.")


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if not cities:
        bot.send_message(message.chat.id, "У тебя пока нет сохранённых городов.")
        return
    path = f"cities_{message.chat.id}.png"
    manager.create_grapf(path, cities)
    with open(path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


if __name__=="__main__":
    manager = DB_Map(DATABASE)
    bot.polling()
