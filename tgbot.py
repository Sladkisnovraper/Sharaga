   main()
    
import telepot
import logging
import requests
from bs4 import BeautifulSoup

# Функция для получения ссылки на последнюю таблицу расписания
def get_latest_schedule_link():
    url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a")
    for link in links:
        if "РАСПИСАНИЕ ЗАНЯТИЙ ОТДЕЛЕНИЯ СПСИПБ" in link.text:
            schedule_url = link.get("href")
            return schedule_url
    return None

# Функция для отправки расписания пользователю
def send_schedule(chat_id):
    # Получаем ссылку на последнюю таблицу расписания
    schedule_url = get_latest_schedule_link()
    if schedule_url:
        bot.sendMessage(chat_id, "Ссылка на последнюю таблицу расписания: " + schedule_url)
    else:
        bot.sendMessage(chat_id, "Не удалось найти ссылку на расписание.")

# Функция для обработки сообщений
def handle_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        command = msg['text']
        if command == '/start':
            on_start(chat_id)
        elif command == '/get_schedule':
            on_get_schedule(chat_id)
        else:
            on_unknown(chat_id)

# Функция для обработки команды /start
def on_start(chat_id):
    bot.sendMessage(chat_id, "Привет! Чтобы получить ссылку на последнюю таблицу расписания, введите /get_schedule.")

# Функция для обработки команды /get_schedule
def on_get_schedule(chat_id):
    # Отправляем ссылку на таблицу расписания
    bot.sendMessage(chat_id, "Ссылка на таблицу расписания: https://tcek63.ru/studentam/raspisanie-zanyatiy/")
    # Запрашиваем у пользователя желание получить ссылку на последнюю таблицу автоматически
    bot.sendMessage(chat_id, "Хочешь автоматом? Если да, напиши 'Да'.")

# Функция для обработки ответа пользователя на предложение получить ссылку на таблицу автоматически
def handle_auto_schedule_request(chat_id, answer):
    if answer.lower() == 'да':
        schedule_url = get_latest_schedule_link()
        if schedule_url:
            bot.sendMessage(chat_id, "Последняя таблица расписания: " + schedule_url)
        else:
            bot.sendMessage(chat_id, "Не удалось найти ссылку на последнюю таблицу расписания.")

# Функция для обработки неизвестных команд
def on_unknown(chat_id):
    bot.sendMessage(chat_id, "Извините, я не понимаю эту команду.")

# Создание и запуск бота
def main():
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    # Получение токена вашего бота
    TOKEN = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

    # Создание экземпляра бота
    global bot
    bot = telepot.Bot(TOKEN)

    # Регистрация обработчика сообщений
    bot.message_loop({'chat': handle_message,
                      'text': handle_auto_schedule_request})

    # Бот начинает работу
    print('Бот запущен. Для выхода нажмите Ctrl+C')
    while True:
        pass

if __name__ == '__main__':
    main()
    
