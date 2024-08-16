from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot_setup import message_router, form_router, logger, redis_conn
from utils import get_crypto_price


class SetCrypto(StatesGroup):
    crypto = State()
    min_price = State()
    max_price = State()


@message_router.message(CommandStart())
async def send_welcome(message: types.Message):
    chat_id = message.chat.id
    logger.info(f"Bot started by user {chat_id}")
    await message.reply("Привет! Нажмите кнопку 'Установить криптовалюту' для начала.",
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=[
                                [KeyboardButton(text="Установить криптовалюту")]
                            ],
                            resize_keyboard=True
                        ))


@message_router.message(lambda message: message.text == "Установить криптовалюту")
async def start_setting_crypto(message: types.Message, state: FSMContext):
    await state.set_state(SetCrypto.crypto)
    logger.info(f"User {message.chat.id} started setting crypto")
    await message.reply("Введите название криптовалюты (например, BTC):")


@form_router.message(SetCrypto.crypto)
async def set_crypto(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(f"Current state before setting crypto: {current_state}")
    await state.update_data(crypto=message.text)
    try:
        await get_crypto_price(message.text)
        logger.info(f"Data after setting crypto: {await state.get_data()}")
        await state.set_state(SetCrypto.min_price)
        current_state = await state.get_state()
        logger.info(f"Current state after setting crypto: {current_state}")
        await message.reply("Введите минимальный порог:")
    except Exception as e:
        logger.error(f"Error setting crypto: {e}")
        await message.reply("Криптовалюта не найдена. Попробуйте еще раз.")


@form_router.message(SetCrypto.min_price)
async def set_min_price(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(f"Current state before setting min price: {current_state}")
    await state.update_data(min_price=float(message.text))
    logger.info(f"Data after setting min price: {await state.get_data()}")
    logger.info(f"User {message.chat.id} set min price to {message.text}")
    await state.set_state(SetCrypto.max_price)
    current_state = await state.get_state()
    logger.info(f"Current state after setting min price: {current_state}")
    await message.reply("Введите максимальный порог:")


@form_router.message(SetCrypto.max_price)
async def set_max_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    crypto = data['crypto']
    min_price = data['min_price']
    max_price = float(message.text)
    logger.info(f"User {message.chat.id} set max price to {message.text} for {crypto}")

    await redis_conn.hset(f"crypto:{message.chat.id}:{crypto}",
                          mapping={"min_price": min_price, "max_price": max_price})

    await state.clear()
    await message.reply(f'Отслеживание {crypto} установлено: минимум {min_price}, максимум {max_price}.')
