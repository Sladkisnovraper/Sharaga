import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext):
    # Отправляем сообщение о начале поиска расписания
    update.message.reply_text("Начинаю поиск расписания...")
    
    # Вызываем функцию для открытия страницы, нажатия на кнопку и скриншота
    open_and_capture_screenshot(update, context)

# Функция для открытия страницы, нажатия на кнопку и скриншота
def open_and_capture_screenshot(update: Update, context: CallbackContext):
    # Запускаем Chrome WebDriver с помощью webdriver_manager
    driver = webdriver.Chrome(ChromeDriverManager().install())
    
    # Открываем страницу с расписанием
    driver.get("https://tcek63.ru/studentam/raspisanie-zanyatiy/")
    
    try:
        # Находим кнопку "РАСПИСАНИЕ ЗАНЯТИЙ ОТДЕЛЕНИЯ СПСИПБ" и кликаем на неё
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "РАСПИСАНИЕ ЗАНЯТИЙ ОТДЕЛЕНИЯ СПСИПБ"))
        )
        button.click()
        
        # Делаем паузу перед выполнением следующих действий, чтобы страница успела загрузиться
        time.sleep(3)
        
        # Находим таблицу с расписанием
        table = driver.find_element_by_xpath("//table[@class='table table-bordered']")
        
        # Создаем скриншот таблицы
        table.screenshot("schedule_screenshot.png")
        
        # Отправляем скриншот пользователю через бота
        update.message.reply_photo(open("schedule_screenshot.png", 'rb'))
        
        # Закрываем браузер после выполнения всех действий
        driver.quit()
        
    except Exception as e:
        # В случае ошибки выводим сообщение об ошибке
        update.message.reply_text(f"Произошла ошибка: {e}")

def main() -> None:
    # Создаем экземпляр класса Updater и передаем ему токен
    updater = Updater("6594143932:AAEwYI8HxNfFPpCRqjEKz9RngAfcUvmnh8M")

    # Получаем диспетчер сообщений бота
    dispatcher = updater.dispatcher

    # Регистрируем обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запускаем бота
    updater.start_polling()

    # Бот будет работать, пока вы не остановите его явно
    updater.idle()

if name == 'main':
    main()
