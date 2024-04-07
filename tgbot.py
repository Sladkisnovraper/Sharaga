import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import re

# Установка уровня логгирования для отображения отладочных сообщений в терминале
logging.basicConfig(level=logging.INFO)

# Функция для получения ссылки на профиль пользователя Telegram
def get_user_profile_link(chat_id, username):
    if username:
        return f"https://t.me/{username}"
    else:
        return f"https://t.me/user{chat_id}"

# Функция для получения сокращенного расписания и ссылок на таблицы
def get_shortened_schedule_info():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        logging.info("Запрос страницы расписания...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_contents = []
        schedule_links = []
        for a in schedule_table.find_all('a'):
            content = a.text.strip()  # Удаляем лишние пробелы
            link = a['href']
            # Находим дату и текст в скобках
            date_text = re.search(r'(\d{2}\.\d{2}\.\d{4}).*?\((.*?)\)', content)
            if date_text:
                date, text = date_text.groups()
                schedule_contents.append(f"{date} ({text})")
                schedule_links.append(link)
        return schedule_contents, schedule_links
    except Exception as e:
        logging.error(f"Ошибка при получении сокращенного содержимого расписания: {e}")
        return None, None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_content, schedule_link):
    message = f"{schedule_content}\n{schedule_link}"
    bot.send_message(user_id, message)
    logging.info(f"Отправлено расписание пользователю {get_user_profile_link(user_id, None)}")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание клавиатуры с кнопкой "Стартуем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton('Стартуем')
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Нажмите 'Стартуем', чтобы начать.", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Обработчик нажатия кнопки "Стартуем"
@bot.message_handler(func=lambda message: message.text == 'Стартуем')
def handle_start_button(message):
    # Получение сокращенного расписания и ссылок
    schedule_contents, schedule_links = get_shortened_schedule_info()
    if schedule_contents and schedule_links:
        # Создание клавиатуры с кнопками содержания расписания
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for content in schedule_contents:
            keyboard.add(types.KeyboardButton(content))
        bot.send_message(message.chat.id, "Выберите дату:", reply_markup=keyboard)
        logging.info(f"Отправлена клавиатура с кнопками содержания расписания пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить сокращенное содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении сокращенного содержимого расписания или ссылок на таблицы.")

# Обработчик нажатия кнопок содержания расписания
@bot.message_handler(func=lambda message: True)
def handle_day_button(message):
    # Получение сокращенного расписания и ссылок
    schedule_contents, schedule_links = get_shortened_schedule_info()
    if schedule_contents and schedule_links:
        chosen_day_content = message.text
        chosen_day_index = schedule_contents.index(chosen_day_content)
        send_schedule_to_user(bot, message.chat.id, chosen_day_content, schedule_links[chosen_day_index])
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить сокращенное содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении сокращенного содержимого расписания или ссылок на таблицы.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
