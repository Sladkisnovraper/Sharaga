import logging
import requests
from bs4 import BeautifulSoup
import telebot

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
    # Получение содержимого ссылок и самих ссылок на расписание
    schedule_contents, schedule_links = get_schedule_info()

    # Отправка содержимого расписания и ссылок на таблицы пользователю в личные сообщения
    if schedule_contents and schedule_links:
        send_schedule_to_user(bot, message.from_user.id, schedule_contents, schedule_links)
    else:
        bot.send_message(message.from_user.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
