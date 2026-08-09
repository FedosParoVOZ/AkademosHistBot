import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ============================================
# НАСТРОЙКИ
# ============================================
TOKEN = "8927630579:AAEVeXYYm4sND5pa2czRRka0bTfi0a9sLJI"  # ← ВСТАВЬТЕ СВОЙ ТОКЕН

CHANNEL_ID = "-1003793088609"
CHANNEL_LINK = "https://t.me/akademos_ist"
COURSE_LINK = "https://akademos.zenclass.ru/public/course/39fa7b7f-f00b-4878-b04e-1938a437b20e"

# FSM для хранения состояния пользователя
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# ============================================
# СОСТОЯНИЯ (FSM)
# ============================================
class UserState(StatesGroup):
    waiting_for_course = State()  # когда пользователь выбрал курс

# ============================================
# ПРОВЕРКА ПОДПИСКИ
# ============================================
async def check_subscribe(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# ============================================
# КОМАНДА /start
# ============================================
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_name = message.from_user.first_name

    # 1. ПРИВЕТСТВИЕ
    await message.answer(
        f"Привет, {user_name}! Ты попал в бот по истории школы Akademos.\n\n"
        "Здесь можно узнать больше об олимпиадах по истории, а также о наших курсах."
    )

    # 2. ПРЕДЛОЖЕНИЯ (зелёная кнопка)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Летний курс ко всош и перечням",
            callback_data="course_summer",  # ← теперь это callback, а не ссылка
            style="success"  # 🟢 ЗЕЛЁНЫЙ ФОН
        )]
    ])

    await message.answer(
        "Выберите курс:",
        reply_markup=keyboard
    )

    # Сохраняем состояние, что пользователь на стадии выбора курса
    await state.set_state(UserState.waiting_for_course)

# ============================================
# ОБРАБОТКА ВСЕХ КНОПОК
# ============================================
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # ========================================
    # КНОПКА "ЛЕТНИЙ КУРС" (ШАГ 1 → ШАГ 2)
    # ========================================
    if callback.data == "course_summer":
        # Сохраняем, какой курс выбрал пользователь
        await state.update_data(selected_course="summer")

        # Проверяем подписку
        if await check_subscribe(user_id):
            # ЕСЛИ УЖЕ ПОДПИСАН → СРАЗУ ДАЁМ ССЫЛКУ
            await callback.message.edit_text(
                "Отлично! Вы уже подписаны на канал.\n\n"
                "Вот ссылка на курс:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Перейти к курсу",
                        url=COURSE_LINK,
                        style="success"
                    )]
                ])
            )
            await callback.answer()
        else:
            # ЕСЛИ НЕ ПОДПИСАН → ПОКАЗЫВАЕМ КНОПКИ ПОДПИСКИ
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Подписаться на канал",
                    url=CHANNEL_LINK,
                    style="primary"  # 🔵 СИНИЙ ФОН
                )],
                [InlineKeyboardButton(
                    text="Проверить подписку",
                    callback_data="check_subscribe",
                    style="primary"  # 🔵 СИНИЙ ФОН
                )]
            ])

            await callback.message.edit_text(
                "Для получения материалов нужно быть подписанным на наш канал.",
                reply_markup=keyboard
            )
            await callback.answer()
        return

    # ========================================
    # КНОПКА "ПРОВЕРИТЬ ПОДПИСКУ" (ШАГ 2 → ШАГ 3)
    # ========================================
    if callback.data == "check_subscribe":
        if await check_subscribe(user_id):
            # ✅ ПОДПИСАЛСЯ → ОТПРАВЛЯЕМ ССЫЛКУ НА КУРС
            # Получаем, какой курс выбрал пользователь
            user_data = await state.get_data()
            selected = user_data.get("selected_course", "summer")

            if selected == "summer":
                course_text = "Летний курс ко всош и перечням"
                course_url = COURSE_LINK

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"Перейти к курсу",
                    url=course_url,
                    style="success"  # 🟢 ЗЕЛЁНЫЙ ФОН
                )]
            ])

            await callback.message.edit_text(
                f"Спасибо за подписку!\n\n"
                f"Вот ссылка на курс:",
                reply_markup=keyboard
            )
            await callback.answer()
        else:
            # ❌ НЕ ПОДПИСАН
            await callback.answer(
                "Вы ещё не подписались на канал. Подпишитесь и нажмите кнопку снова.",
                show_alert=True
            )
        return

    await callback.answer()

# ============================================
# ЗАПУСК
# ============================================
async def main():
    print("=" * 50)
    print("БОТ ЗАПУЩЕН!")
    print(f"Канал: {CHANNEL_LINK}")
    print("=" * 50)
    print("Бот готов к работе. Нажмите Ctrl+C для остановки.")
    print("=" * 50)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())