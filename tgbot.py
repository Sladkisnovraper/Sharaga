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
            message = f"Содержание расписания: {content}\nСсылка на таблицу: {link}"
            bot.send_message(user_id, message)
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания или ссылки на таблицы.")

# Функция для удаления сообщений бота с расписанием и ссылками
def delete_schedule_messages(bot, chat_id, message_ids):
    for message_id in message_ids:
        bot.delete_message(chat_id, message_id)

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Словарь для хранения идентификаторов сообщений с расписанием и ссылками по каждому пользователю
user_schedule_messages = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_schedule = types.KeyboardButton('Го узнаем')
    keyboard.add(button_schedule)
    
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)

# Обработчик нажатия кнопки "Го узнаем"
@bot.message_handler(func=lambda message: message.text == 'Го узнаем')
def handle_schedule_button(message):
    # Получение содержимого ссылок и самих ссылок на расписание
    schedule_contents, schedule_links = get_schedule_info()

    # Отправка содержимого расписания и ссылок на таблицы пользователю в личные сообщения
    if schedule_contents and schedule_links:
        sent_message = send_schedule_to_user(bot, message.from_user.id, schedule_contents, schedule_links)
        # Сохраняем идентификаторы отправленных сообщений
        if sent_message:
            user_schedule_messages[message.from_user.id] = sent_message.message_id
        # Меняем клавиатуру
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_delete = types.KeyboardButton('Заебало сотри это')
        keyboard.add(button_delete)
        bot.send_message(message.chat.id, "Вот тебе расписание, если что, можешь удалить", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")

# Обработчик нажатия кнопки "Заебало сотри это"
@bot.message_handler(func=lambda message: message.text == 'Заебало сотри это')
def handle_delete_button(message):
    # Получаем идентификаторы отправленных сообщений с расписанием и ссылками
    message_ids = user_schedule_messages.get(message.from_user.id)
    if message_ids:
        # Удаляем сообщения
        delete_schedule_messages(bot, message.chat.id, [message_ids])
        bot.send_message(message.chat.id, "Сообщения с расписанием удалены.")
    else:
        bot.send_message(message.chat.id, "Не найдено сообщений с расписанием для удаления.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
