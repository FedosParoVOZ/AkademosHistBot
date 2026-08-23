import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден!")

# ========== ТРИ КАНАЛА ==========
CHANNEL_ID_1 = "-1003793088609"    # @akademos_ist
CHANNEL_ID_2 = "-1004294233096"    # @akadem_os
CHANNEL_ID_3 = "-1002778589667"   # @НОВЫЙ_КАНАЛ (ЗАМЕНИ НА РЕАЛЬНЫЙ ID!)

CHANNEL_LINK_1 = "https://t.me/akademos_ist"
CHANNEL_LINK_2 = "https://t.me/akadem_os"
CHANNEL_LINK_3 = "https://t.me/iusspb"   # ЗАМЕНИ НА ССЫЛКУ

# ========== ССЫЛКИ НА КУРСЫ ==========
SUMMER_COURSE_LINK = "https://akademos.zenclass.ru/public/course/39fa7b7f-f00b-4878-b04e-1938a437b20e"  # Летний курс (требует подписки)
MAIN_COURSE_LINK = "https://akademos.zenclass.ru/courses/73dcc2de-c8bf-440c-884e-4c22ad95381d/edit/structure"  # Основной курс (без подписки)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_sub(user_id):
    """Проверяет подписку на все 3 канала"""
    try:
        m1 = await bot.get_chat_member(CHANNEL_ID_1, user_id)
        m2 = await bot.get_chat_member(CHANNEL_ID_2, user_id)
        m3 = await bot.get_chat_member(CHANNEL_ID_3, user_id)
        
        return (m1.status in ["member", "creator"] and
                m2.status in ["member", "creator"] and
                m3.status in ["member", "creator"])
    except:
        return False

# ========== КНОПКИ ==========
def main_menu():
    """Главное меню: основной курс (без подписки) и летний курс (с подпиской)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Основной курс",
            url=MAIN_COURSE_LINK,
            style="primary"
        )],
        [InlineKeyboardButton(
            text="Летний курс ко всош и перечням",
            callback_data="summer_course",
            style="success"
        )]
    ])

def summer_course_buttons():
    """Кнопки для летнего курса: 3 подписки + проверка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Подписаться на канал по истории",
            url=CHANNEL_LINK_1,
            style="primary"
        )],
        [InlineKeyboardButton(
            text="Подписаться на канал Академос",
            url=CHANNEL_LINK_2,
            style="primary"
        )],
        [InlineKeyboardButton(
            text="Подписаться на Петербургское право",
            url=CHANNEL_LINK_3,
            style="primary"
        )],
        [InlineKeyboardButton(
            text="Проверить подписку",
            callback_data="check_sub",
            style="primary"
        )]
    ])

def summer_course_link():
    """Зелёная кнопка со ссылкой на летний курс"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Перейти к летнему курсу",
            url=SUMMER_COURSE_LINK,
            style="success"
        )]
    ])

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer(
        f"Привет, {msg.from_user.first_name}! Ты попал в бот по истории школы Akademos.\n\n"
        "Здесь можно узнать больше об олимпиадах по истории, а также о наших курсах."
    )
    await msg.answer(
        "Выберите курс:",
        reply_markup=main_menu()
    )

@dp.callback_query()
async def click(call: types.CallbackQuery):
    uid = call.from_user.id

    # ===== НАЖАЛИ НА ЛЕТНИЙ КУРС =====
    if call.data == "summer_course":
        if await check_sub(uid):
            await call.message.edit_text(
                "Отлично! Вы подписаны на все каналы.\n\nВот ссылка на летний курс:",
                reply_markup=summer_course_link()
            )
        else:
            await call.message.edit_text(
                "Для доступа к летнему курсу нужно быть подписанным на все наши каналы:",
                reply_markup=summer_course_buttons()
            )
        await call.answer()
        return

    # ===== НАЖАЛИ НА ПРОВЕРКУ ПОДПИСКИ =====
    if call.data == "check_sub":
        if await check_sub(uid):
            await call.message.edit_text(
                "Спасибо за подписку!\n\nВот ссылка на летний курс:",
                reply_markup=summer_course_link()
            )
        else:
            await call.answer(
                "Вы ещё не подписались на все каналы.\nПодпишитесь и нажмите кнопку снова.",
                show_alert=True
            )
        return

async def main():
    print("=" * 50)
    print("🤖 БОТ ЗАПУЩЕН")
    print(f"📢 Канал 1: {CHANNEL_LINK_1}")
    print(f"📢 Канал 2: {CHANNEL_LINK_2}")
    print(f"📢 Канал 3: {CHANNEL_LINK_3}")
    print("=" * 50)
    print("🔓 Основной курс: доступен без подписки")
    print("🔒 Летний курс: требует подписки на 3 канала")
    print("=" * 50)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
