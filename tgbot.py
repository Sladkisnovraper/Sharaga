import logging
import requests
from bs4 import BeautifulSoup
import telebot

# Функция для получения ссылок на таблицы и текст из 6-й ячейки
def get_table_info():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        
        # Создаем список кортежей, каждый кортеж содержит ссылку и текст из 6-й ячейки таблицы
        table_info = []
        for row in schedule_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 6:  # Проверяем наличие шестой ячейки
                link = cells[5].text.strip()  # Получаем текст ссылки из шестой ячейки
                table_info.append((link, cells[5].text.strip()))  # Добавляем ссылку и текст в список
        return table_info
    except Exception as e:
        print(f"Ошибка при получении ссылок на таблицы: {e}")
        return None

# Функция для отправки информации пользователю в личные сообщения
def send_info_to_user(bot, user_id, table_info):
    if table_info:
        for link, text in table_info:
            bot.send_message(user_id, f"Текст из 6-й ячейки: {text}\nСсылка на таблицу: {link}")
    else:
        bot.send_message(user_id, "Не удалось найти информацию.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Чтобы получить информацию о расписании, используй команду /schedule.")

# Обработчик команды /schedule
@bot.message_handler(commands=['schedule'])
def send_schedule_command(message):
    # Получение информации о таблицах
    table_info = get_table_info()

    # Отправка информации пользователю в личные сообщения
    if table_info:
        send_info_to_user(bot, message.from_user.id, table_info)
    else:
        bot.send_message(message.from_user.id, "Ошибка: не удалось получить информацию о расписании.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
