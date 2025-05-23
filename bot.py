import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Замените на ваш токен бота
BOT_TOKEN = "8106053896:AAHYZxtt-jTvMcR1ltaMQOtS9wRojCMpy68"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для FSM
class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()

# Клавиатура с inline кнопками
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="📝 Регистрация", callback_data="register")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])
    return keyboard

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Я простой Telegram бот, созданный с помощью aiogram 3.x\n"
        f"Выберите действие:",
        reply_markup=get_main_keyboard()
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
🤖 <b>Команды бота:</b>

/start - Запуск бота
/help - Показать это сообщение
/echo - Повторить ваше сообщение
/stats - Показать статистику
/register - Начать регистрацию

<b>Inline кнопки:</b>
• Статистика - показывает информацию о боте
• Настройки - настройки пользователя
• Регистрация - процесс регистрации
• Помощь - справочная информация
    """
    await message.answer(help_text, parse_mode="HTML")

# Обработчик команды /echo
@dp.message(Command("echo"))
async def cmd_echo(message: Message):
    text = message.text.replace("/echo", "").strip()
    if text:
        await message.answer(f"🔄 Вы написали: <i>{text}</i>", parse_mode="HTML")
    else:
        await message.answer("📝 Напишите что-нибудь после команды /echo")

# Обработчики inline кнопок
@dp.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    stats_text = f"""
📊 <b>Статистика бота:</b>

👤 Ваш ID: <code>{callback.from_user.id}</code>
👤 Имя: {callback.from_user.first_name}
👤 Username: @{callback.from_user.username or 'не указан'}
🤖 Версия aiogram: 3.x
⚡ Статус: Активен
    """
    await callback.message.edit_text(stats_text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    settings_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
        [InlineKeyboardButton(text="🌍 Язык", callback_data="language")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\nВыберите параметр для изменения:",
        parse_mode="HTML",
        reply_markup=settings_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "register")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Давайте зарегистрируем вас!\n\nКак вас зовут?")
    await state.set_state(UserStates.waiting_for_name)
    await callback.answer()

@dp.callback_query(F.data == "help")
async def show_help_inline(callback: CallbackQuery):
    help_text = """
ℹ️ <b>Справка</b>

Этот бот демонстрирует возможности aiogram 3.x:
• Обработка команд
• Inline клавиатуры
• FSM (машина состояний)
• Обработка callback'ов
• Парсинг сообщений

<b>Создан с использованием:</b>
🐍 Python
🤖 aiogram 3.x
    """
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text(help_text, parse_mode="HTML", reply_markup=back_keyboard)
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        f"👋 Привет, {callback.from_user.first_name}!\n\n"
        f"Я простой Telegram бот, созданный с помощью aiogram 3.x\n"
        f"Выберите действие:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

# Обработчики для регистрации (FSM)
@dp.message(UserStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Приятно познакомиться, {message.text}! 😊\n\nТеперь скажите, сколько вам лет?")
    await state.set_state(UserStates.waiting_for_age)

@dp.message(UserStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 0 or age > 150:
            await message.answer("🤔 Пожалуйста, введите корректный возраст (от 0 до 150)")
            return
        
        data = await state.get_data()
        name = data.get("name")
        
        await message.answer(
            f"✅ <b>Регистрация завершена!</b>\n\n"
            f"👤 Имя: {name}\n"
            f"🎂 Возраст: {age} лет\n\n"
            f"Спасибо за регистрацию! 🎉",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите возраст числом")

# Обработчик неизвестных callback'ов
@dp.callback_query()
async def unknown_callback(callback: CallbackQuery):
    await callback.answer("❓ Неизвестная команда", show_alert=True)

# Обработчик всех остальных сообщений
@dp.message()
async def echo_message(message: Message):
    if message.text:
        await message.answer(
            f"💬 Вы написали: <i>{message.text}</i>\n\n"
            f"Используйте /help для просмотра доступных команд",
            parse_mode="HTML"
        )
    else:
        await message.answer("🤔 Я понимаю только текстовые сообщения")

# Главная функция
async def main():
    logger.info("Запуск бота...")
    
    # Удаляем старые апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")