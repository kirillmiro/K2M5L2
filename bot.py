import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)
manager = DB_Map(DATABASE)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """
Доступные команды:
/start - приветствие!
/help - список команд.
/show_city <city_name> [цвет] - показать город на карте.
/remember_city <city_name> [цвет] - сохранить город с указанным цветом.
/show_my_cities - показать все твои сохранённые города.
Доступные цвета: red, blue, green, yellow, orange, purple
""")

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /show_city <название> [цвет]")
        return
    
    city_name = parts[1]
    color = parts[2] if len(parts) > 2 else "red"

    path = f"city_{message.chat.id}.png"
    result = manager.create_grapf(path, [(city_name, color)])
    if result:
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.send_message(message.chat.id, "Такого города нет в базе.")

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /remember_city <название> [цвет]")
        return
    
    user_id = message.chat.id
    city_name = parts[1]
    color = parts[2] if len(parts) > 2 else "red"

    if manager.add_city(user_id, city_name, color):
        bot.send_message(message.chat.id, f'Город {city_name} сохранён с цветом {color}!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities_with_colors = manager.select_cities(message.chat.id)
    if not cities_with_colors:
        bot.send_message(message.chat.id, "У тебя пока нет сохранённых городов.")
        return

    path = f"cities_{message.chat.id}.png"
    manager.create_grapf(path, cities_with_colors)
    with open(path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

if __name__ == "__main__":
    bot.polling()
