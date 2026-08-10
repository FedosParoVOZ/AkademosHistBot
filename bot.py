import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ============================================
# НАСТРОЙКИ
# ============================================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен не найден! Добавьте переменную TELEGRAM_BOT_TOKEN в Railway.")

# ID каналов
CHANNEL_ID_1 = "-1003793088609"   # @akademos_ist
CHANNEL_ID_2 = "-1004294233096"   # @akadem_os

# Ссылки на каналы
CHANNEL_LINK_1 = "https://t.me/akademos_ist"
CHANNEL_LINK_2 = "https://t.me/akadem_os"

# Ссылка на курс
COURSE_LINK = "https://akademos.zenclass.ru/public/course/39fa7b7f-f00b-4878-b04e-1938a437b20e"

# ============================================
# НАСТРОЙКА БОТА
# ============================================
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ============================================
# СОСТОЯНИЯ
# ============================================
class UserState(StatesGroup):
    waiting_for_course = State()

# ============================================
# ПРОВЕРКА ПОДПИСКИ (НА ОБА КАНАЛА)
# ============================================
async def check_subscribe(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на оба канала."""
    try:
        # Проверяем первый канал
        member_1 = await bot.get_chat_member(chat_id=CHANNEL_ID_1, user_id=user_id)
        if member_1.status not in ['member', 'creator']:
            print(f"❌ Пользователь {user_id} не подписан на канал {CHANNEL_ID_1}")
            return False

        # Проверяем второй канал
        member_2 = await bot.get_chat_member(chat_id=CHANNEL_ID_2, user_id=user_id)
        if member_2.status not in ['member', 'creator']:
            print(f"❌ Пользователь {user_id} не подписан на канал {CHANNEL_ID_2}")
            return False

        # Подписан на оба
        print(f"✅ Пользователь {user_id} подписан на оба канала")
        return True

    except Exception as e:
        print(f"⚠️ Ошибка проверки подписки для {user_id}: {e}")
        return False

# ============================================
# КЛАВИАТУРЫ
# ============================================
def get_course_keyboard():
    """Кнопка с ссылкой на курс (зелёная)."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Перейти к курсу",
            url=COURSE_LINK,
            style="success"
        )]
    ])
    return keyboard

def get_subscribe_keyboard():
    """Три синие кнопки: две для подписки на каналы и одна для проверки."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
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
            text="Проверить подписку",
            callback_data="check_subscribe",
            style="primary"
        )]
    ])
    return keyboard

def get_main_keyboard():
    """Главное меню с кнопкой курса."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Летний курс ко всош и перечням",
            callback_data="course_summer",
            style="success"
        )]
    ])
    return keyboard

# ============================================
# КОМАНДА /start
# ============================================
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_name = message.from_user.first_name

    await message.answer(
        f"Привет, {user_name}! Ты попал в бот по истории школы Akademos.\n\n"
        "Здесь можно узнать больше об олимпиадах по истории, а также о наших курсах."
    )

    await message.answer(
        "Выберите курс:",
        reply_markup=get_main_keyboard()
    )
    await state.set_state(UserState.waiting_for_course)

# ============================================
# ОБРАБОТКА КНОПОК
# ============================================
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # ===== КНОПКА "ЛЕТНИЙ КУРС" =====
    if callback.data == "course_summer":
        await state.update_data(selected_course="summer")

        if await check_subscribe(user_id):
            # ✅ ПОДПИСАН НА ОБА КАНАЛА
            await callback.message.edit_text(
                "Отлично! Вы подписаны на оба канала.\n\nВот ссылка на курс:",
                reply_markup=get_course_keyboard()
            )
            await callback.answer()
        else:
            # ❌ НЕ ПОДПИСАН ХОТЯ БЫ НА ОДИН
            await callback.message.edit_text(
                "Для получения материалов нужно быть подписанным на наши каналы:",
                reply_markup=get_subscribe_keyboard()
            )
            await callback.answer()
        return

    # ===== КНОПКА "ПРОВЕРИТЬ ПОДПИСКУ" =====
    if callback.data == "check_subscribe":
        if await check_subscribe(user_id):
            # ✅ ПОДПИСАЛСЯ НА ОБА
            await callback.message.edit_text(
                "Спасибо за подписку!\n\nВот ссылка на курс:",
                reply_markup=get_course_keyboard()
            )
            await callback.answer()
        else:
            # ❌ ВСЁ ЕЩЁ НЕ ПОДПИСАН
            await callback.answer(
                "Вы ещё не подписались на все каналы.\n"
                "Подпишитесь и нажмите кнопку снова.",
                show_alert=True
            )
        return

    await callback.answer()

# ============================================
# ЗАПУСК
# ============================================
async def main():
    print("=" * 50)
    print("🤖 БОТ ЗАПУЩЕН НА RAILWAY!")
    print(f"📢 Канал 1: {CHANNEL_LINK_1}")
    print(f"📢 Канал 2: {CHANNEL_LINK_2}")
    print("=" * 50)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
