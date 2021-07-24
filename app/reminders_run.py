import asyncio
import sqlite3
from datetime import datetime

from aiogram import Bot

from app.config_reader import load_config

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()

bot = Bot(token=config.bot.TOKEN)


async def check():
    cur.execute("SELECT * FROM reminders;")
    reminders_results = cur.fetchall()
    #
    time = datetime.utcnow().strftime("%H:%M")
    for x in reminders_results:
        if x[4] == time:
            if x[6] == 'onetime':
                cur.execute("DELETE FROM reminders WHERE id=%s;" % str(x[0]))
                conn.commit()
                await bot.send_message(chat_id=x[1], text=x[5])
            #
            else:
                days = [bool(int(y)) for y in x[6].split('|')]
                if days[datetime.utcnow().weekday()]:
                    await bot.send_message(chat_id=x[1], text=x[5])
    #
    await asyncio.sleep(60)
    await check()


async def start():
    current_sec = int(datetime.now().strftime("%S"))
    delay = 60 - current_sec
    if delay == 0:
        delay = 0
    #
    await asyncio.sleep(delay)
    await check()
