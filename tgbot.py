import logging
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types

# Функция для получения содержимого ссылок и самих ссылок на расписание
def get_schedule_info():
    try:
        # Замените URL на ссылку, которую вы указали
        url = "https://tcek63.ru/studentam/raspisanie-zanyatiy/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        schedule_table = soup.find('table', class_='acc_body')
        schedule_contents = [a.text for a in schedule_table.find_all('a')]
        schedule_links = [a['href'] for a in schedule_table.find_all('a')]
        return schedule_contents, schedule_links
    except Exception as e:
        print(f"Ошибка при получении содержимого ссылок на расписание: {e}")
        return None, None

# Основная функция бота
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

    # Обработчик нажатия кнопки "Стартуем"
    @bot.message_handler(func=lambda message: message.text == 'Стартуем')
    def handle_start_button(message):
        # Получение содержимого расписания и ссылок на таблицы
        schedule_contents, schedule_links = get_schedule_info()

        # Отправка содержимого расписания и ссылок на таблицы пользователю в личные сообщения
        if schedule_contents and schedule_links:
            for content, link in zip(schedule_contents, schedule_links):
                # Получение текста из таблицы (замените на нужную логику)
                text_from_sheet = "Текст из таблицы G25-G34"
                if text_from_sheet:
                    # Отправка сообщения с расписанием и текстом из таблицы
                    message = f"Содержание расписания: {content}\nСсылка на таблицу: {link}\nТекст из таблицы:\n{text_from_sheet}"
                    bot.send_message(message.chat.id, message)
                else:
                    bot.send_message(message.chat.id, "Ошибка: не удалось получить текст из таблицы.")
        else:
            bot.send_message(message.chat.id, "Ошибка: не удалось получить содержимое расписания или ссылки на таблицы.")

    # Запуск бота
    bot.polling()

if __name__ == "__main__":
    main()
