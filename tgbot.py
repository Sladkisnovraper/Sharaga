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

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Удаление всех кнопок и создание кнопки "Стартуем"
    keyboard = types.ReplyKeyboardRemove()
    button_start = types.KeyboardButton("Стартуем")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Стартуем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Обработчик кнопки "Стартуем"
@bot.message_handler(func=lambda message: message.text == 'Стартуем')
def handle_start_button(message):
    # Создание кнопки "Го узнаем" после нажатия кнопки "Стартуем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_go_learn = types.KeyboardButton("Го узнаем")
    keyboard.add(button_go_learn)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)
    logging.info(f"Отправлена клавиатура с кнопкой 'Го узнаем' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Обработчик кнопки "Го узнаем"
@bot.message_handler(func=lambda message: message.text == 'Го узнаем')
def handle_go_learn_button(message):
    # Получение содержимого расписания и ссылок
    global schedule_contents, schedule_links  # Объявляем глобальные переменные
    schedule_contents, schedule_links = get_schedule_info()  # Обновляем содержимое расписания и ссылки
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
        # Добавление кнопки "Скинь все"
        button_send_all = types.KeyboardButton("Скинь все")
        keyboard.add(button_send_all)
        bot.send_message(message.chat.id, "На какой день?", reply_markup=keyboard)
        logging.info(f"Отправлена клавиатура с кнопками содержания расписания пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")
    else:
        bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")
        logging.warning("Ошибка при получении содержимого расписания или ссылок на таблицы.")

# Обработчик нажатия кнопок с днями недели
@bot.message_handler(func=lambda message: any(message.text.startswith(day) for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]))
def handle_day_button(message):
    chosen_day = message.text
    global schedule_contents, schedule_links  # Объявляем глобальные переменные
    schedule_contents, schedule_links = get_schedule_info()  # Обновляем содержимое расписания и ссылки
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
    # Удаление кнопки "Назад" и создание кнопки "Стартуем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton("Стартуем")
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Нажимай 'Стартуем', чтобы получить расписание", reply_markup=keyboard)
    logging.info(f"Отправлено сообщение 'Нажимай Старт чтобы получить расписание' пользователю {get_user_profile_link(message.chat.id, message.from_user.username)}")

# Обработчик кнопки "Скинь все"
@bot.message_handler(func=lambda message: message.text == 'Скинь все')
def handle_send_all_button(message):
    # Отправка всех расписаний с ссылками на таблицы
    send_schedule_to_user(bot, message.chat.id, schedule_contents, schedule_links)

# Запуск бота
def main():
    global schedule_contents, schedule_links
    schedule_contents, schedule_links = get_schedule_info()  # Получение содержимого расписания и ссылок
    logging.info("Запуск бота...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    main()
