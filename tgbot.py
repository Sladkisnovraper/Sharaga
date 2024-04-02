import logging
import requests
from bs4 import BeautifulSoup
import telebot

# Функция для получения ссылки на расписание
def get_schedule_data():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_data = []
        for row in schedule_table.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                day_of_week = cells[0].text.strip()
                date = cells[1].text.strip()
                schedule_links = [a['href'] for a in cells[2].find_all('a')]
                schedule_data.append((day_of_week, date, schedule_links))
        return schedule_data
    except Exception as e:
        print(f"Ошибка при получении расписания: {e}")
        return None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_data):
    if schedule_data:
        for day_of_week, date, links in schedule_data:
            message = f"<b>{day_of_week}, {date}</b>:\n"
            if links:
                for link in links:
                    message += f"Ссылка на расписание: {link}\n"
            else:
                message += "Расписание отсутствует\n"
            bot.send_message(user_id, message, parse_mode='HTML')
    else:
        bot.send_message(user_id, "Ошибка: не удалось получить расписание.")

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
    # Получение расписания
    schedule_data = get_schedule_data()

    # Отправка расписания пользователю в личные сообщения
    if schedule_data:
        send_schedule_to_user(bot, message.from_user.id, schedule_data)
    else:
        bot.send_message(message.from_user.id, "Ошибка: не удалось получить расписание.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
