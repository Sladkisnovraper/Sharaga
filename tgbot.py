import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# Функция для получения содержимого ссылок и самих ссылок на расписание
def get_schedule_info():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_contents = [a.text for a in schedule_table.find_all('a')]
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_contents, schedule_links
    except Exception as e:
        print(f"Ошибка при получении содержимого ссылок на расписание: {e}")
        return None, None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_contents, schedule_links):
    if schedule_contents and schedule_links:
        for content, link in zip(schedule_contents, schedule_links):
            message = f"{content}\n{link}"
            bot.send_message(user_id, message)
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания или ссылки на таблицы.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton('Стартуем')
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Кнопку 'Старт' нажимай", reply_markup=keyboard)

# Обработчик нажатия кнопки "Стартуем"
@bot.message_handler(func=lambda message: message.text == 'Стартуем')
def handle_start_button(message):
    # Создание клавиатуры с кнопкой "Го узнаем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_schedule = types.KeyboardButton('Го узнаем')
    keyboard.add(button_schedule)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)

# Обработчик нажатия кнопки "Го узнаем"
@bot.message_handler(func=lambda message: message.text == 'Го узнаем')
def handle_schedule_button(message):
    # Создание клавиатуры с кнопками дней недели
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    buttons = [types.KeyboardButton(day) for day in days]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "На какой день?", reply_markup=keyboard)

# Обработчик нажатия кнопок дней недели
@bot.message_handler(func=lambda message: message.text in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"])
def handle_day_button(message):
    # Получение содержимого расписания и ссылок
    schedule_contents, schedule_links = get_schedule_info()
    # Отправка расписания на выбранный день
    if schedule_contents and schedule_links:
        day = message.text.upper()  # Приводим к верхнему регистру, чтобы сравнивать с текстом в расписании
        day_schedule_contents = [content for content, link in zip(schedule_contents, schedule_links) if day in content]
        day_schedule_links = [link for content, link in zip(schedule_contents, schedule_links) if day in content]
        send_schedule_to_user(bot, message.chat.id, day_schedule_contents, day_schedule_links)
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
    
