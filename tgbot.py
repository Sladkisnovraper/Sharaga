import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# Функция для получения содержимого ссылок и самих ссылок на расписание
def get_schedule_info():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_contents = [a.text for a in schedule_table.find_all('a')]
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_contents, schedule_links
    except Exception as e:
        print(f"Ошибка при получении содержимого ссылок на расписание: {e}")
        return None, None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_contents, schedule_links):
    if schedule_contents and schedule_links:
        # Проверяем, есть ли какие-либо данные в расписании
        if len(schedule_contents) > 0 and len(schedule_links) > 0:
            # Отправляем только последние 6 элементов
            for content, link in zip(schedule_contents[-6:], schedule_links[-6:]):
                message = f"Содержание расписания: {content}\nСсылка на таблицу: {link}"
                bot.send_message(user_id, message)
        else:
            bot.send_message(user_id, "Расписание пусто.")
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания или ссылки на таблицы.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton('Стартуем')
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Привет! Нажми кнопку 'Стартуем', чтобы начать", reply_markup=keyboard)

# Обработчик нажатия кнопки "Стартуем"
@bot.message_handler(func=lambda message: message.text == 'Стартуем')
def handle_start_button(message):
    # Создание клавиатуры с кнопкой "Го узнаем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_schedule = types.KeyboardButton('Го узнаем')
    keyboard.add(button_schedule)
    bot.send_message(message.chat.id, "Че там по расписанию?", reply_markup=keyboard)

# Обработчик нажатия кнопки "Го узнаем"
@bot.message_handler(func=lambda message: message.text == 'Го узнаем')
def handle_schedule_button(message):
    # Получение содержимого ссылок и самих ссылок на расписание
    schedule_contents, schedule_links = get_schedule_info()

    # Проверка на наличие содержимого расписания и ссылок
    if schedule_contents and schedule_links and len(schedule_contents) > 0 and len(schedule_links) > 0:
        # Отправка содержимого расписания и ссылок на таблицы пользователю в личные сообщения
        send_schedule_to_user(bot, message.from_user.id, schedule_contents, schedule_links)

        # Удаление кнопки "Го узнаем"
        bot.send_message(message.chat.id, "Вот тебе расписание, если что, можешь нажать кнопку 'Стартуем', чтобы вернуться к началу.", reply_markup=types.ReplyKeyboardRemove())
        
        # Создание клавиатуры с кнопкой "Стартуем"
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_start = types.KeyboardButton('Стартуем')
        keyboard.add(button_start)
        bot.send_message(message.chat.id, "Нажми кнопку 'Стартуем', чтобы начать заново", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Расписание пусто или не удалось получить информацию о расписании.")

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
        
