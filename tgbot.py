import logging
import requests
from bs4 import BeautifulSoup
import telebot

# Функция для получения ссылки на расписание
def get_schedule_link():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_links
    except Exception as e:
        print(f"Ошибка при получении ссылки на расписание: {e}")
        return None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_links):
    if schedule_links:
        for link in schedule_links:
            bot.send_message(user_id, f"Ссылка на расписание: {link}")
    else:
        bot.send_message(user_id, "Не удалось найти ссылку на расписание.")

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
    # Получение ссылок на расписание
    schedule_links = get_schedule_link()

    # Отправка расписания пользователю в личные сообщения
    if schedule_links:
        send_schedule_to_user(bot, message.from_user.id, schedule_links)
    else:
        bot.send_message(message.from_user.id, "Ошибка: не удалось получить ссылки на расписание.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
