import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# Функция для получения содержимого указанных ячеек Google таблицы
def get_google_sheet_data(sheet_url):
    try:
        response = requests.get(sheet_url)
        soup = BeautifulSoup(response.content, "html.parser")
        # Находим ячейки G25-G34
        cells = soup.find_all('div', {'class': 'grid-table-container'})[0].find_all('div', {'class': 'cell'})[24:34]
        cell_contents = [cell.text for cell in cells]
        return cell_contents
    except Exception as e:
        print(f"Ошибка при получении данных из Google таблицы: {e}")
        return None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_contents, schedule_links):
    if schedule_contents and schedule_links:
        for content, link in zip(schedule_contents, schedule_links):
            # Получение содержимого указанных ячеек Google таблицы для каждой ссылки
            google_sheet_data = get_google_sheet_data(link)
            
            message = f"Содержание расписания: {content}\nСсылка на таблицу: {link}\n\n"
            if google_sheet_data:
                message += "Содержимое ячеек G25-G34:\n"
                message += "\n".join(google_sheet_data)
            bot.send_message(user_id, message)
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания или ссылки на таблицы.")

# Получение токена вашего бота
bot_token = '6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

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
    # Получение ссылок на расписание
    schedule_contents, schedule_links = get_schedule_info()

    # Отправка содержимого расписания и ссылок на таблицы пользователю в личные сообщения
    send_schedule_to_user(bot, message.from_user.id, schedule_contents, schedule_links)

    # Удаление кнопки "Го узнаем"
    bot.send_message(message.chat.id, "Вот тебе расписание, если что, можешь нажать кнопку 'Стартуем', чтобы вернуться к началу.", reply_markup=types.ReplyKeyboardRemove())

    # Создание клавиатуры с кнопкой "Стартуем"
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_start = types.KeyboardButton('Стартуем')
    keyboard.add(button_start)
    bot.send_message(message.chat.id, "Нажми кнопку 'Стартуем', чтобы начать заново", reply_markup=keyboard)

# Основная функция
def main():
    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
