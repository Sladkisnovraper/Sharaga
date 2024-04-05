import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import time

# Установка уровня логгирования для отображения отладочных сообщений в терминале
logging.basicConfig(level=logging.INFO)

# Функция для получения ссылки на профиль пользователя Telegram
def get_user_profile_link(chat_id, username):
    if username:
        return f"https://t.me/{username}"
    else:
        return f"https://t.me/user{chat_id}"

# Функция для получения содержимого ссылок и самих ссылок на расписание
def get_schedule_info():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        logging.info("Запрос страницы расписания...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_contents = [a.text for a in schedule_table.find_all('a')]
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_contents, schedule_links
    except Exception as e:
        logging.error(f"Ошибка при получении содержимого ссылок на расписание: {e}")
        return None, None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_contents, schedule_links):
    if schedule_contents and schedule_links:
        for content, link in zip(schedule_contents, schedule_links):
            message = f"{content}\n{link}"
            bot.send_message(user_id, message)
            logging.info(f"Отправлено расписание пользователю {get_user_profile_link(user_id, None)}")
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания или ссылки на таблицы.")
        logging.warning("Не удалось найти содержимое расписания или ссылки на таблицы.")

# Функция для проверки времени бездействия пользователя
def check_user_activity(last_activity_time):
    current_time = time.time()
    inactive_time = current_time - last_activity_time
    return inactive_time

# Функция для отправки сообщения о времени до отключения
def send_time_remaining_message(chat_id, remaining_time):
    bot.send_message(chat_id, f"До отключения бота осталось {int(remaining_time)} секунд.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Словарь для хранения времени последнего активного взаимодействия пользователя
last_activity = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton('Стартуем')
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Кнопку 'Старт' нажимай", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    # Сохранение времени активности пользователя
    last_activity[message.chat.id] = time.time()

# Обработчик нажатия кнопки "Стартуем"
@bot.message_handler(func=lambda message: message.text == 'Стартуем')
def handle_start_button(message):
    # Создание клавиатуры с кнопкой "Го узнаем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_schedule = types.KeyboardButton('Го узнаем')
    keyboard.add(button_schedule)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Го узнаем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    # Сохранение времени активности пользователя
    last_activity[message.chat.id] = time.time()

# Обработчик нажатия кнопки "Го узнаем"
@bot.message_handler(func=lambda message: message.text == 'Го узнаем')
def handle_schedule_button(message):
    # Создание клавиатуры с кнопками дней недели
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
    buttons = [types.KeyboardButton(day) for day in days]
    keyboard.add(*buttons)
    # Добавление кнопок "Скинуть все" и "Назад"
    button_reset = types.KeyboardButton("Скинуть все")
    button_back = types.KeyboardButton("Назад")
    keyboard.add(button_reset, button_back)
    bot.send_message(message.chat.id, "На какой день?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопками дней недели пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    # Сохранение времени активности пользователя
    last_activity[message.chat.id] = time.time()

# Обработчик нажатия кнопок дней недели
@bot.message_handler(func=lambda message: message.text in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"])
def handle_day_button(message):
    # Получение содержимого расписания и ссылок
    schedule_contents, schedule_links = get_schedule_info()
    # Отправка расписания на выбранный день
    if schedule_contents and schedule_links:
        day = message.text.upper()  # Приводим к верхнему регистру, чтобы сравнивать с текстом в расписании
        day_schedule_contents = [content for content, link in zip(schedule_contents, schedule_links) if day in content]
        day_schedule_links = [link for content, link in zip(schedule_contents, schedule_links) if day in content]
        send_schedule_to_user(bot, message.chat.id, day_schedule_contents, day_schedule_links)
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении содержимого расписания или ссылок на таблицы.")
    # Сохранение времени активности пользователя
    last_activity[message.chat.id] = time.time()

# Обработчик нажатия кнопки "Скинуть все"
@bot.message_handler(func=lambda message: message.text == 'Скинуть все')
def handle_reset_button(message):
    # Получение содержимого расписания и ссылок
    schedule_contents, schedule_links = get_schedule_info()
    # Отправка всего расписания
    if schedule_contents and schedule_links:
        send_schedule_to_user(bot, message.chat.id, schedule_contents, schedule_links)
        # Удаление кнопки "Скинуть все"
        bot.send_message(message.chat.id, "Расписание отправлено.")
        logging.info(f"Отправлено расписание пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
        # Добавление кнопки "Назад"
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_back = types.KeyboardButton('Назад')
        keyboard.add(button_back)
        bot.send_message(message.chat.id, "Нажмите 'Назад', чтобы вернуться.", reply_markup=keyboard)
        logging.info(f"Отправлена клавиатура с кнопкой 'Назад' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении содержимого расписания или ссылок на таблицы.")
    # Сохранение времени активности пользователя
    last_activity[message.chat.id] = time.time()

# Обработчик нажатия кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == 'Назад')
def handle_back_button(message):
    # Удаление всех кнопок кроме кнопки "Стартуем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton('Стартуем')
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Нажмите 'Стартуем', чтобы начать заново.", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Стартуем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    # Сохранение времени активности пользователя
    last_activity[message.chat.id] = time.time()

# Обработчик сообщений для отслеживания бездействия пользователя
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.id in last_activity:
        inactive_time = check_user_activity(last_activity[message.chat.id])
        logging.info(f"Пользователь {get_user_profile_link(message.chat.id, message.from_user.username)} бездействует уже {inactive_time} секунд.")
        if inactive_time > 600:  # 10 минут бездействия
            bot.send_message(message.chat.id, "Вы были неактивны слишком долго. Пожалуйста, нажмите 'Стартуем', чтобы начать заново.")
            logging.info(f"Пользователь {get_user_profile_link(message.chat.id, message.from_user.username)} был отключен из-за длительного бездействия.")
            del last_activity[message.chat.id]  # Удаление времени последнего активного взаимодействия
    else:
        logging.warning(f"Нет данных о последнем активном времени пользователя {get_user_profile_link(message.chat.id, message.from_user.username)}.")

# Функция для проверки времени бездействия пользователя и отправки сообщения о времени до отключения
def check_inactive_users():
    while True:
        for chat_id, last_activity_time in last_activity.items():
            inactive_time = check_user_activity(last_activity_time)
            if inactive_time > 600:  # 10 минут бездействия
                bot.send_message(chat_id, "Вы были неактивны слишком долго. Пожалуйста, нажмите 'Стартуем', чтобы начать заново.")
                logging.info(f"Пользователь {get_user_profile_link(chat_id, None)} был отключен из-за длительного бездействия.")
                del last_activity[chat_id]  # Удаление времени последнего активного взаимодействия
            else:
                remaining_time = 600 - inactive_time
                logging.info(f"До отключения пользователя {get_user_profile_link(chat_id, None)} осталось {int(remaining_time)} секунд.")
        time.sleep(20)  # Проверяем каждые 20 секунд

# Основная функция
def main():
    # Запуск бота
    bot.polling()

    # Запуск функции для проверки времени бездействия пользователя
    check_inactive_users()

if __name__ == "__main__":
    main()
    
