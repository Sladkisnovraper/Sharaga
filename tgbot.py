import logging
import requests
from bs4 import BeautifulSoup
import telebot

# Функция для получения содержимого ссылок на расписание
def get_schedule_content():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_contents = [a.text for a in schedule_table.find_all('a')]
        return schedule_contents
    except Exception as e:
        print(f"Ошибка при получении содержимого ссылок на расписание: {e}")
        return None

# Функция для отправки содержимого расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_contents):
    if schedule_contents:
        for content in schedule_contents:
            bot.send_message(user_id, f"Содержание расписания: {content}")
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Го чекнем че по расписанию?")

# Обработчик команды /schedule
@bot.message_handler(commands=['schedule'])
def send_schedule_command(message):
    # Получение содержимого ссылок на расписание
    schedule_contents = get_schedule_content()

    # Отправка содержимого расписания пользователю в личные сообщения
    if schedule_contents:
        send_schedule_to_user(bot, message.from_user.id, schedule_contents)
    else:
        bot.send_message(message.from_user.id, "Ошибка: не удалось получить содержимое расписания.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
