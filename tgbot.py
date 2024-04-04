import logging
import subprocess
from bs4 import BeautifulSoup
import telebot
from telebot import types

# Функция для получения содержимого ссылок и самих ссылок на расписание
def get_schedule_info():
    try:
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = subprocess.run(["w3m", "-dump", url], capture_output=True, text=True)
        soup = BeautifulSoup(response.stdout, "html.parser")
        schedule_table = soup.find_all('div', class_='acc_body')[3].find('table').find('tbody')
        schedule_contents = [a.text for a in schedule_table.find_all('a')]
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_contents, schedule_links
    except Exception as e:
        print(f"Ошибка при получении содержимого ссылок на расписание: {e}")
        return None, None

# Функция для отправки расписания пользователю в личные сообщения
def send_schedule_to_user(bot, user_id, schedule_contents, schedule_links, screenshots):
    if schedule_contents and schedule_links:
        for content, link, screenshot in zip(schedule_contents, schedule_links, screenshots):
            message = f"Содержание расписания: {content}\nСсылка на таблицу: {link}"
            bot.send_message(user_id, message)
            bot.send_photo(user_id, open(screenshot, 'rb'))
    else:
        bot.send_message(user_id, "Не удалось найти содержимое расписания или ссылки на таблицы.")

# Основная функция
def main():
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

    # Обработчик нажатия кнопки "Го узнаем"
    @bot.message_handler(func=lambda message: message.text == 'Го узнаем')
    def handle_schedule_button(message):
        # Получение содержимого ссылок и самих ссылок на расписание
        schedule_contents, schedule_links = get_schedule_info()
        screenshots = []

        # Отправка содержимого расписания и ссылок на таблицы пользователю в личные сообщения
        if schedule_contents and schedule_links:
            for link in schedule_links:
                screenshot_path = f"{link.split('/')[-1]}.png"
                subprocess.run(["w3m", "-dump", "-o", "ext_image_viewer=1", "-o", f"imgdisplay_path=~/storage/shared/{screenshot_path}", link])
                screenshots.append(screenshot_path)
            send_schedule_to_user(bot, message.from_user.id, schedule_contents, schedule_links, screenshots)
            # Удаление кнопки "Го узнаем"
            bot.send_message(message.chat.id, "Вот тебе расписание, если что, можешь нажать кнопку 'Стартуем', чтобы вернуться к началу.", reply_markup=types.ReplyKeyboardRemove())
            # Создание клавиатуры с кнопкой "Стартуем"
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_start = types.KeyboardButton('Стартуем')
            keyboard.add(button_start)
            bot.send_message(message.chat.id, "Нажми кнопку 'Стартуем', чтобы начать заново", reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")

    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
