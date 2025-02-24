import logging
import os
import re
import asyncio
import sqlite3
import tempfile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes,
    MessageHandler, filters
)
from pydub import AudioSegment
import speech_recognition as sr

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

TOKEN = 'ВАШ_ТОКЕН'  # ⚠️ Замените на свой токен

# Инициализация SQLite
conn = sqlite3.connect('user_states.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        video_path TEXT
    )
''')
conn.commit()

def add_punctuation(text):
    if not text:
        return ""
    if text[-1] not in '.!?':
        return text.capitalize() + '.'
    return text.capitalize()

async def check_ffmpeg():
    try:
        await asyncio.create_subprocess_exec(
            'ffmpeg', '-version',
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
    except FileNotFoundError:
        logger.error('FFmpeg не установлен!')
        raise RuntimeError("FFmpeg не найден")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет, я могу сделать из видео кружок или голосовое сообщение, а также расшифровать их в текст.'
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        video = update.message.video
        if video.file_size > 2 * 1024 * 1024 * 1024:
            await update.message.reply_text('Видео слишком большое (макс. 2 ГБ)')
            return

        video_file = video.file_id
        file = await context.bot.get_file(video_file)
        
        video_path = os.path.join('video_storage', f"{video_file}.mp4")
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        
        await file.download_to_drive(video_path)
        
        cursor.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', 
                      (update.message.from_user.id, video_path))
        conn.commit()

        keyboard = [
            [
                InlineKeyboardButton("Кружок", callback_data='video_note'),
                InlineKeyboardButton("Голосовое", callback_data='voice_message')
            ]
        ]
        await update.message.reply_text(
            'Выберите действие:', 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f'Ошибка обработки видео: {str(e)}')
        await update.message.reply_text('Произошла ошибка при обработке видео')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    
    cursor.execute('SELECT video_path FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        await query.answer('Видео не найдено!')
        return
    
    video_path = result[0]
    
    try:
        if query.data == 'video_note':
            await process_video_note(query, video_path)
        elif query.data == 'voice_message':
            await process_voice_message(query, video_path)
            
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        conn.commit()
        
    except Exception as e:
        logger.error(f'Ошибка обработки запроса: {str(e)}')
        await query.message.reply_text('Произошла ошибка при обработке')

async def process_video_note(query, video_path):
    try:
        msg = await query.message.reply_text('⏳ Обработка видео...')
        
        output_path = tempfile.mktemp(suffix='.mp4')
        command = [
            'ffmpeg', '-i', video_path,
            '-vf', 'crop=in_h:in_h,scale=240:240',
            '-c:a', 'copy', output_path
        ]
        
        proc = await asyncio.create_subprocess_exec(*command, stderr=asyncio.subprocess.PIPE)
        await track_progress(proc, msg, 'Обработка видео')
        
        with open(output_path, 'rb') as f:
            await query.message.reply_video_note(f)
            
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

async def process_voice_message(query, video_path):
    try:
        msg = await query.message.reply_text('⏳ Извлечение аудио...')
        
        output_path = tempfile.mktemp(suffix='.ogg')
        command = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', output_path]
        
        proc = await asyncio.create_subprocess_exec(*command, stderr=asyncio.subprocess.PIPE)
        await track_progress(proc, msg, 'Конвертация аудио')
        
        with open(output_path, 'rb') as f:
            await query.message.reply_voice(f)
            
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

async def track_progress(proc, msg, prefix):
    while True:
        line = await proc.stderr.readline()
        if not line:
            break
            
        if time_match := re.search(r'time=(\d+:\d+:\d+\.\d+)', line.decode()):
            current_time = time_match.group(1)
            await msg.edit_text(f'{prefix}: {current_time}')
            
    await msg.edit_text('✅ Готово!')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        with tempfile.NamedTemporaryFile(suffix='.ogg') as ogg_file:
            await file.download_to_drive(ogg_file.name)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(ogg_file.name) as source:
                audio = recognizer.record(source)
                
            text = recognizer.recognize_google(audio, language='ru-RU')
            text = add_punctuation(text)
            
            await update.message.reply_text(f'**Текст:**\n{text}', parse_mode='Markdown')
            
    except sr.UnknownValueError:
        await update.message.reply_text('Не удалось распознать речь')
    except sr.RequestError:
        await update.message.reply_text('Ошибка сервиса распознавания')
    except Exception as e:
        logger.error(f'Ошибка распознавания: {str(e)}')
        await update.message.reply_text('Ошибка обработки аудио')

def main():
    # Исправление ошибки с event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(check_ffmpeg())
        
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.VIDEO, handle_video))
        app.add_handler(MessageHandler(filters.VOICE, handle_audio))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info('Бот запущен')
        app.run_polling()
    finally:
        loop.close()

if __name__ == '__main__':
    os.makedirs('video_storage', exist_ok=True)
    main()
