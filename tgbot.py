import telepot
import logging
import requests
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

# Функция для получения ссылки на последнюю таблицу расписания
def get_latest_schedule_link():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a")
        for link in links:
            if "РАСПИСАНИЕ ЗАНЯТИЙ ОТДЕЛЕНИЯ СПСИПБ" in link.text:
                schedule_url = link.get("href")
                return schedule_url
        logging.error("Не удалось получить ссылку на расписание")
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении ссылки на расписание: {e}")
        return None

# Функция для отправки расписания пользователю
def send_schedule(chat_id):
    schedule_url = get_latest_schedule_link()
    if schedule_url:
        bot.sendMessage(chat_id, "Ссылка на последнюю таблицу расписания: " + schedule_url)
    else:
        bot.sendMessage(chat_id, "Не удалось найти ссылку на расписание.")

# Функция для проверки доступности сайта
def check_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return "Сайт доступен."
        else:
            return f"Сайт недоступен. Статус код: {response.status_code}"
    except Exception as e:
        return f"Ошибка при проверке доступности сайта: {e}"

# Функция для обработки сообщений
def handle_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        command = msg['text']
        if command == '/start':
            on_start(chat_id)
        elif command == '/get_schedule':
            on_get_schedule(chat_id)
        elif command == '/auto':
            on_auto(chat_id)
        elif command == '/check':
            on_check(chat_id)
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
    bot.sendMessage(chat_id, "Хочешь автоматом? Если да, напиши /auto.")

# Функция для обработки команды /auto
def on_auto(chat_id):
    send_schedule(chat_id)
    bot.sendMessage(chat_id, "Теперь давай проверим доступность сайта. Если хочешь проверить, напиши /check.")

# Функция для обработки команды /check
def on_check(chat_id):
    website_url = "https://tcek63.ru/"
    result = check_website(website_url)
    bot.sendMessage(chat_id, result)

# Функция для обработки неизвестных команд
def on_unknown(chat_id):
    bot.sendMessage(chat_id, "Извините, я не понимаю эту команду.")

# Создание и запуск бота
def main():
    # Получение токена вашего бота
    TOKEN = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

    # Создание экземпляра бота
    global bot
    bot = telepot.Bot(TOKEN)

    # Регистрация обработчика сообщений
    bot.message_loop({'chat': handle_message})

    # Бот начинает работу
    logging.info('Бот запущен. Для выхода нажмите Ctrl+C')
    while True:
        pass

if __name__ == '__main__':
    main()
