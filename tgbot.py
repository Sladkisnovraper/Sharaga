import telepot
import logging
import requests
from bs4 import BeautifulSoup

# Функция для получения ссылки на последнюю таблицу расписания
def get_schedule_link():
    url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a")
    for link in links:
        if "РАСПИСАНИЕ ЗАНЯТИЙ ОТДЕЛЕНИЯ СПСИПБ" in link.text:
            schedule_url = link.get("href")
            return schedule_url
    return None

# Функция для проверки доступности ссылки
def check_schedule_link(schedule_url):
    try:
        response = requests.head(schedule_url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print("Ошибка при проверке доступности ссылки:", e)
        return False

# Функция для получения текста из ячеек 25-34 из таблицы расписания
def get_schedule_text(schedule_url):
    response = requests.get(schedule_url)
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    last_table = tables[-1]  # Последняя таблица
    rows = last_table.find_all("tr")
    schedule_text = ""
    for row in rows[24:34]:
        cells = row.find_all("td")
        for cell in cells:
            schedule_text += cell.text.strip() + "\n"
    return schedule_text

# Функция для отправки расписания пользователю
def send_schedule(chat_id):
    schedule_url = get_schedule_link()
    if schedule_url:
        if check_schedule_link(schedule_url):
            schedule_text = get_schedule_text(schedule_url)
            bot.sendMessage(chat_id, schedule_text)
        else:
            bot.sendMessage(chat_id, "Ссылка на расписание недоступна.")
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
    bot.sendMessage(chat_id, "Привет! Для получения расписания введите /get_schedule")

# Функция для обработки команды /get_schedule
def on_get_schedule(chat_id):
    send_schedule(chat_id)

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
    bot.message_loop(handle_message)

    # Бот начинает работу
    print('Бот запущен. Для выхода нажмите Ctrl+C')
    while True:
        pass

if __name__ == '__main__':
    main()
    
