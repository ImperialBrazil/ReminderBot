import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import load_config
from app.handlers.common import register_handlers_common
from app.handlers.del_reminder import register_handlers_del_reminder
from app.handlers.edit_reminder import register_handlers_edit_reminder
from app.handlers.lang import register_handlers_lang
from app.handlers.my_reminders import register_handlers_my_reminders
from app.handlers.set_reminder import register_handlers_set_reminder
from app.handlers.utc import register_handlers_utc
from datetime import datetime
from app import reminders_run

logger = logging.getLogger(__name__)


async def main(loop):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    #
    config = load_config("config/bot.ini")
    open(config.bot.way, 'a+')
    conn = sqlite3.connect(config.bot.way)
    cur = conn.cursor()
    #
    cur.execute('''CREATE TABLE IF NOT EXISTS "users" (
    "user_chat_id"	INTEGER,
    "lang"	TEXT,
    "utc_code"	REAL,
    "new_reminder"	INTEGER,
    "reminder_id"	INTEGER,
    PRIMARY KEY("user_chat_id")
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "reminders" (
    "id"	INTEGER,
    "user_chat_id"	INTEGER,
    "local_time"	TEXT,
    "local_days"	TEXT,
    "time"	TEXT,
    "text"	TEXT,
    "days"	TEXT,
    PRIMARY KEY("id")
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "keyboard" (
    "user_chat_id"	INTEGER,
    "Monday"	TEXT,
    "Tuesday"	TEXT,
    "Wednesday"	TEXT,
    "Thursday"	TEXT,
    "Friday"	TEXT,
    "Saturday"	TEXT,
    "Sunday"	TEXT,
    PRIMARY KEY("user_chat_id")
    )''')
    conn.commit()
    #
    bot = Bot(token=config.bot.TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    #
    register_handlers_common(dp)
    register_handlers_utc(dp)
    register_handlers_set_reminder(dp)
    register_handlers_my_reminders(dp)
    register_handlers_lang(dp)
    register_handlers_del_reminder(dp)
    register_handlers_edit_reminder(dp)
    asyncio.ensure_future(reminders_run.start())
    #
    await dp.start_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
