import telebot
import logging
import requests
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# Токен вашего бота
TOKEN = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Функция для получения ссылки на последнюю таблицу расписания
def get_latest_schedule_link():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find('div', class_='acc_body').find('table')
        if schedule_table:
            schedule_link = schedule_table.find('tr', class_='head').find('a')['href']
            return schedule_link
        else:
            logging.error("Не удалось найти ссылку на таблицу расписания")
            return None
    except Exception as e:
        logging.error(f"Ошибка при получении ссылки на расписание: {e}")
        return None

# Функция для отправки расписания пользователю
def send_schedule(chat_id):
    schedule_url = get_latest_schedule_link()
    if schedule_url:
        bot.send_message(chat_id, f"Ссылка на последнюю таблицу расписания: {schedule_url}")
    else:
        bot.send_message(chat_id, "Не удалось найти ссылку на расписание.")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Чтобы получить ссылку на последнюю таблицу расписания, введите /get_schedule.')

# Обработчик команды /get_schedule
@bot.message_handler(commands=['get_schedule'])
def get_schedule(message):
    send_schedule(message.chat.id)

# Запуск бота
bot.polling()
