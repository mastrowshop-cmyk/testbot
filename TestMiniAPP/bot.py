import asyncio
import sqlite3
from datetime import datetime
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, MenuButtonWebApp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            phone TEXT,
            name TEXT,
            client_code TEXT UNIQUE,
            role TEXT DEFAULT 'client',
            registered_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY,
            track TEXT,
            user_id INTEGER,
            location TEXT,
            status TEXT DEFAULT 'ожидает',
            weight REAL,
            price REAL,
            added_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
user_data = {}

@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('delivery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "👋 *Добро пожаловать!*\n\nДля регистрации поделитесь номером телефона:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await show_main_menu(message, user)

@dp.message(F.contact)
async def get_contact(message: Message):
    user_id = message.from_user.id
    contact = message.contact
    user_data[user_id] = {"phone": contact.phone_number}
    await message.answer(
        f"📱 *Номер получен:* {contact.phone_number}\n\nВведите ваше *имя и фамилию*:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if user_id in user_data and "phone" in user_data[user_id]:
        if "name" not in user_data[user_id]:
            user_data[user_id]["name"] = text
            await message.answer(f"👤 *Имя:* {text}\n\nВведите *код клиента*:", parse_mode="Markdown")
        elif "code" not in user_data[user_id]:
            client_code = text
            conn = sqlite3.connect('delivery.db')
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (telegram_id, phone, name, client_code, registered_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, user_data[user_id]["phone"], user_data[user_id]["name"], 
                      client_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                await message.answer(f"🎉 *Регистрация завершена!*\nКод: {client_code}", parse_mode="Markdown")
                await show_main_menu(message)
            except sqlite3.IntegrityError:
                await message.answer("❌ Код уже используется")
            finally:
                conn.close()
                if user_id in user_data:
                    del user_data[user_id]
    else:
        await message.answer("Используйте приложение через кнопку ниже")

async def show_main_menu(message: Message, user=None):
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="🚀 ОТКРЫТЬ ПРИЛОЖЕНИЕ", 
                web_app=WebAppInfo(url=f"{WEB_APP_URL}?user_id={user_id}")
            )
        ]]
    )
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(
            text="📱 Приложение", 
            web_app=WebAppInfo(url=f"{WEB_APP_URL}?user_id={user_id}")
        )
    )
    await message.answer(
        "📦 *Доставка Якутск*\n\nНажмите кнопку чтобы открыть приложение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def main():
    print("🤖 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())