from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Функция для отправки скриншота пользователю в Telegram
def send_screenshot(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, "Ищу расписание...")

    # Настройки браузера
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    # Переход по ссылке и поиск расписания
    driver.get("https://tcek63.ru/studentam/raspisanie-zanyatiy/")
    search_element = driver.find_element(By.PARTIAL_LINK_TEXT, "РАСПИСАНИЕ ЗАНЯТИЙ ОТДЕЛЕНИЯ СПСИПБ")
    search_element.click()

    # Ожидание загрузки страницы
    time.sleep(5)

    # Поиск ссылки на таблицу с расписанием
    links = driver.find_elements(By.TAG_NAME, "a")
    last_link = links[-1]
    last_link.click()

    # Ожидание загрузки таблицы
    time.sleep(5)

    # Создание скриншота
    driver.save_screenshot("schedule_screenshot.png")

    # Отправка скриншота пользователю
    context.bot.send_photo(chat_id, photo=open("schedule_screenshot.png", "rb"))

    # Закрытие браузера
    driver.quit()

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Для получения расписания введите /get_schedule")

# Создание и запуск бота
def main():
    updater = Updater("6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get_schedule", send_screenshot))
    updater.start_polling()
    updater.idle()

if name == 'main':
    main()
