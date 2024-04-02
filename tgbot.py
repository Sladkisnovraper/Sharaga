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
        schedule_table = soup.find('div', class_='acc_body').find('table').find('tbody')
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_links
    except Exception as e:
        print(f"Ошибка при получении ссылки на расписание: {e}")
        return None

# Функция для отправки расписания пользователю
def send_schedule(bot, schedule_links):
    if schedule_links:
        for link in schedule_links:
            bot.send_message(bot.get_me().id, f"Ссылка на расписание: {link}")
    else:
        bot.send_message(bot.get_me().id, "Не удалось найти ссылку на расписание.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Основная функция
def main():
    # Получение ссылок на расписание
    schedule_links = get_schedule_link()

    # Отправка расписания пользователю
    if schedule_links:
        send_schedule(bot, schedule_links)
    else:
        print("Ошибка: не удалось получить ссылки на расписание.")

if __name__ == "__main__":
    main()
