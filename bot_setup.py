import os
from dotenv import load_dotenv
import redis.asyncio as aioredis
from aiogram import Router, Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger


load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_conn = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

bot = Bot(token=API_TOKEN)
storage = RedisStorage(redis=redis_conn)
dp = Dispatcher(storage=storage)
message_router = Router()
form_router = Router()

logger.add("crypto_bot.log",
           format="{time} {level} {message}",
           rotation="10 MB",
           compression='zip',
           level="DEBUG")
