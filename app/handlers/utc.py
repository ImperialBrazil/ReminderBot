import sqlite3
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.config_reader import load_config
from app.keyboards import UTC_keyboard
from app.localization import lang
from app.utc_time import time_operation

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()


class UTC(StatesGroup):
    start = State()
    waiting_for_time_zone = State()


async def cmd_utc(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    user_data = cur.fetchone()
    #
    await message.delete()
    await message.answer(lang[user_data[1]]['utc_new'] % user_data[2], reply_markup=UTC_keyboard(lang[user_data[1]]),
                         parse_mode=types.ParseMode.HTML)
    await UTC.waiting_for_time_zone.set()


async def time_zone_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % call.message.chat.id)
    user_data = cur.fetchone()
    #
    if call.data != 'cancel':
        cur.execute('SELECT * FROM reminders WHERE user_chat_id = %s' % call.message.chat.id)
        reminders_results = list(cur.fetchall())
        # Time
        greenwich_time = str(datetime.utcnow().time())[0:5]
        utc_code = call.data[3:9]
        if utc_code[0] == '+':
            utc_code = '-' + utc_code[1::]
        elif utc_code[0] == '−':
            utc_code = '+' + utc_code[1::]
        local_time, a, b = time_operation(greenwich_time, utc_code, False, False, False, False, False, False, False)
        #
        if reminders_results:
            for x in range(len(reminders_results)):
                if str(reminders_results[x][3]) != 'onetime':
                    local_days = str(reminders_results[x][3]).split('|')
                    time, local_days, days = time_operation(reminders_results[x][2], call.data[3:9], *local_days)
                else:
                    time, local_days, days = time_operation(reminders_results[x][2], call.data[3:9],
                                                            False, False, False, False, False, False, False)
                    days = 'onetime'
                cur.execute('UPDATE reminders SET time = ?, days = ? Where id = ?',
                            (time, days, reminders_results[x][0]))
        #
        await call.message.edit_text(lang[user_data[1]]['utc_result'] % (('<code>UTC' + call.data[3:9] + '</code>'),
                                                                         '<code>' + local_time + '</code>'),
                                     parse_mode=types.ParseMode.HTML)
        cur.execute("UPDATE users SET utc_code = ? WHERE user_chat_id = ?", (call.data[3::], call.message.chat.id))
        conn.commit()
    else:
        await call.message.edit_text(lang[user_data[1]]['successfully'])
    #
    await call.answer()
    await UTC.first()


def register_handlers_utc(dp: Dispatcher):
    dp.register_message_handler(cmd_utc, commands="utc", state="*")
    dp.register_callback_query_handler(time_zone_choose, state=UTC.waiting_for_time_zone)
