import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

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

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Обработчик кнопки "Стартуем"
@bot.message_handler(func=lambda message: message.text == 'Стартуем')
def handle_start_button(message):
    bot.send_message(message.chat.id, "Выполняю команду /start...")
    handle_start(message)  # Вызываем функцию обработки команды /start

# Функция для обработки команды /start
def handle_start(message):
    # Удаление кнопки "Стартуем" и создание кнопки "Го узнаем"
    keyboard = types.ReplyKeyboardRemove()
    button_go_learn = types.KeyboardButton("Го узнаем")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_go_learn)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Го узнаем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Удаление кнопки "Стартуем" и создание кнопки "Го узнаем"
    keyboard = types.ReplyKeyboardRemove()
    button_go_learn = types.KeyboardButton("Го узнаем")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_go_learn)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Го узнаем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Обработчик кнопки "Го узнаем"
@bot.message_handler(func=lambda message: message.text == 'Го узнаем')
def handle_go_learn_button(message):
    # Получение содержимого расписания и ссылок
    schedule_contents, schedule_links = get_schedule_info()
    if schedule_contents and schedule_links:
        # Создание клавиатуры с днями недели
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        unique_days = set()  # Множество для хранения уникальных дней недели
        for content in schedule_contents:
            # Поиск даты и дня недели в содержании расписания
            date_day = find_date_and_day(content)
            if date_day:
                date, day = date_day
                if day is not None:  # Проверка наличия дня недели
                    unique_days.add(day)  # Добавление уникального дня недели в множество
                    keyboard.add(types.KeyboardButton(f"{date} ({day})"))
        # Добавление кнопки "Назад"
        button_back = types.KeyboardButton("Назад")
        keyboard.add(button_back)
        bot.send_message(message.chat.id, "На какой день?", reply_markup=keyboard)
        logging.info(f"Отправлена клавиатура с кнопками содержания расписания пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении содержимого расписания или ссылок на таблицы.")

# Функция для поиска даты и дня недели в содержании расписания
def find_date_and_day(content):
    date = None
    day = None
    # Поиск даты в формате "дд.мм.гггг"
    if any(char.isdigit() for char in content):
        date_parts = content.split()
        for part in date_parts:
            if '.' in part and len(part) == 10:  # Проверка на формат даты
                date = part
                break
    # Поиск дня недели
    if '(' in content and ')' in content:
        day_start = content.find('(') + 1
        day_end = content.find(')')
        day = content[day_start:day_end]
    return date, day

# Обработчик нажатия кнопок содержания расписания
@bot.message_handler(func=lambda message: any(message.text.startswith(day) for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]))
def handle_day_button(message):
    chosen_day = message.text
    # Получение содержимого расписания и ссылок
    schedule_contents, schedule_links = get_schedule_info()
    if schedule_contents and schedule_links:
        day_schedule_contents = []
        day_schedule_links = []
        for content, link in zip(schedule_contents, schedule_links):
            date_day = find_date_and_day(content)
            if date_day and date_day[1] in chosen_day:
                day_schedule_contents.append(content)
                day_schedule_links.append(link)
        # Отправка расписания на выбранный день
        send_schedule_to_user(bot, message.chat.id, day_schedule_contents, day_schedule_links)
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении содержимого расписания или ссылок на таблицы.")

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda message: message.text == 'Назад')
def handle_back_button(message):
    # Удаление всех кнопок и отправка клавиатуры с кнопкой "Го узнаем"
    keyboard = types.ReplyKeyboardRemove()
    button_go_learn = types.KeyboardButton("Го узнаем")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_go_learn)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Го узнаем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Запуск бота
def main():
    logging.info("Запуск бота...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
