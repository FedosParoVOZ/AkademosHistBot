import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден!")

CHANNEL_ID_1 = "-1003793088609"
CHANNEL_ID_2 = "-1004294233096"

CHANNEL_LINK_1 = "https://t.me/akademos_ist"
CHANNEL_LINK_2 = "https://t.me/akadem_os"
COURSE_LINK = "https://akademos.zenclass.ru/public/course/39fa7b7f-f00b-4878-b04e-1938a437b20e"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_sub(user_id):
    try:
        m1 = await bot.get_chat_member(CHANNEL_ID_1, user_id)
        m2 = await bot.get_chat_member(CHANNEL_ID_2, user_id)
        return (m1.status in ["member", "creator"] and
                m2.status in ["member", "creator"])
    except:
        return False

# ========== КНОПКИ (БЕЗ СТИЛЕЙ!) ==========
def green_course():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Летний курс ко всош и перечням", callback_data="course")]
    ])

def blue_subscribe():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться на канал по истории", url=CHANNEL_LINK_1)],
        [InlineKeyboardButton(text="Подписаться на канал Академос", url=CHANNEL_LINK_2)],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check")]
    ])

def green_go():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти к курсу", url=COURSE_LINK)]
    ])

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        f"Привет, {msg.from_user.first_name}! Ты попал в бот по истории школы Akademos.\n\n"
        "Здесь можно узнать больше об олимпиадах по истории, а также о наших курсах."
    )
    await msg.answer("Выберите курс:", reply_markup=green_course())

@dp.callback_query()
async def click(call: types.CallbackQuery):
    uid = call.from_user.id

    if call.data == "course":
        if await check_sub(uid):
            await call.message.edit_text(
                "Отлично! Вы подписаны на оба канала.\n\nВот ссылка на курс:",
                reply_markup=green_go()
            )
        else:
            await call.message.edit_text(
                "Для получения материалов нужно быть подписанным на наши каналы:",
                reply_markup=blue_subscribe()
            )
        await call.answer()
        return

    if call.data == "check":
        if await check_sub(uid):
            await call.message.edit_text(
                "Спасибо за подписку!\n\nВот ссылка на курс:",
                reply_markup=green_go()
            )
        else:
            await call.answer(
                "Вы ещё не подписались на все каналы.\nПодпишитесь и нажмите кнопку снова.",
                show_alert=True
            )
        return

async def main():
    print("🤖 БОТ ЗАПУЩЕН")
    print(f"Канал 1: {CHANNEL_LINK_1}")
    print(f"Канал 2: {CHANNEL_LINK_2}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())            
