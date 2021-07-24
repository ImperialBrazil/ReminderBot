import sqlite3

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified

from app.config_reader import load_config
from app.keyboards import DAYS_keyboard
from app.localization import lang
from app.utc_time import time_operation

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()
bot = Bot(token=config.bot.TOKEN)


class SetReminder(StatesGroup):
    start = State()
    waiting_for_time = State()
    waiting_for_days = State()
    waiting_for_text = State()


async def cmd_set_reminder(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % message.chat.id)
    user_results = cur.fetchone()
    #
    await message.delete()
    await message.answer(lang[user_results[1]]['time_enter'])
    #
    await SetReminder.waiting_for_time.set()


async def time_enter(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % message.chat.id)
    user_results = cur.fetchone()
    cur.execute("SELECT * FROM keyboard WHERE user_chat_id = %s;" % message.chat.id)
    keyboard_results = cur.fetchone()
    local = lang[user_results[1]]
    #
    await message.delete()
    #
    try:
        if len(message.text) == 5 and int(message.text[0]) < 3 and int(message.text[1]) < 10 and \
                message.text[2] == ':' and int(message.text[3]) < 6 and int(message.text[4]) < 10 and \
                int(message.text[0:2]) < 24:
            cur.execute("UPDATE users SET new_reminder = ? WHERE user_chat_id = ?",
                        ("None, %s, %s, None, None, None, None" % (message.chat.id, message.text),
                         message.chat.id))
            conn.commit()
            #
            await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                        text=local['choose_days'], reply_markup=DAYS_keyboard(keyboard_results, local))
            await SetReminder.next()
        #
        elif message.text == '/cancel' or message.text == 'cancel':
            await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                        text=local['successfully'])
            await SetReminder.first()
        #
        else:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                        text=local['time_error'])
            await SetReminder.first()
    except ValueError:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                    text=local['time_error'])
        await SetReminder.first()


async def days_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM keyboard WHERE user_chat_id = %s;" % call.message.chat.id)
    keyboard_results = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % call.message.chat.id)
    user_results = cur.fetchone()
    week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    local = lang[user_results[1]]
    #
    if call.data == 'ready':
        if keyboard_results != (call.message.chat.id, '❌', '❌', '❌', '❌', '❌', '❌', '❌'):
            days = [False, False, False, False, False, False, False]
            for x in range(0, 7):
                if keyboard_results[x + 1] == '❌':
                    days[x] = False
                else:
                    days[x] = True
            #
            new_reminder = user_results[3].split(', ')
            time, local_days, days_ = time_operation(new_reminder[2], user_results[2], *days)
            new_reminder[3] = local_days
            new_reminder[4] = time
            new_reminder[6] = days_
            #
            cur.execute('UPDATE users SET new_reminder = ? WHERE user_chat_id = ?;', (str(new_reminder)[1:-1],
                                                                                      call.message.chat.id))
            cur.execute('UPDATE keyboard SET Monday = ?, Tuesday = ?, Wednesday = ?, Thursday = ?, Friday = '
                        '?, Saturday = ?, Sunday= ? WHERE user_chat_id = %s;' % call.message.chat.id,
                        ('❌', '❌', '❌', '❌', '❌', '❌', '❌'))
            conn.commit()
            #
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=local['text_enter'])
            await SetReminder.next()
        else:
            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=local['days_error'], reply_markup=DAYS_keyboard(keyboard_results,
                                                                                                 local))
            except MessageNotModified:
                pass
    #
    elif call.data == 'cancel':
        for v in range(0, 7):
            do = "UPDATE keyboard SET %s = ? WHERE user_chat_id = ?;" % week[v]
            cur.execute(do, ('❌', call.message.chat.id))
        conn.commit()
        #
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=local['successfully'])
        await SetReminder.first()
    #
    elif call.data == 'onetime':
        new_reminder = user_results[3].split(', ')
        time, local_days, days_ = time_operation(new_reminder[2], user_results[2],
                                                 False, False, False, False, False, False, False)
        new_reminder[3] = new_reminder[6] = 'onetime'
        new_reminder[4] = time
        #
        cur.execute('UPDATE users SET new_reminder = ? WHERE user_chat_id = ?;', (str(new_reminder)[1:-1],
                                                                                  call.message.chat.id))
        cur.execute('UPDATE keyboard SET Monday = ?, Tuesday = ?, Wednesday = ?, Thursday = ?, Friday = '
                    '?, Saturday = ?, Sunday= ? WHERE user_chat_id = %s;' % call.message.chat.id,
                    ('❌', '❌', '❌', '❌', '❌', '❌', '❌'))
        conn.commit()
        #
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=local['text_enter'])
        await SetReminder.next()
    #
    else:
        if keyboard_results[int(call.data) + 1] == '❌':
            symbol = '✅'
        else:
            symbol = '❌'
        cur.execute("UPDATE keyboard SET %s = ? WHERE user_chat_id = ?;" % week[int(call.data)],
                    (symbol, call.message.chat.id))
        cur.execute("SELECT * FROM keyboard WHERE user_chat_id = %s;" % call.message.chat.id)
        conn.commit()
        keyboard_results = cur.fetchone()
        #
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=local['choose_days'], reply_markup=DAYS_keyboard(keyboard_results, local))
    #
    await call.answer()


async def text_enter(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % message.chat.id)
    user_results = cur.fetchone()
    cur.execute("SELECT * FROM reminders;")
    reminders_results = cur.fetchall()
    if not reminders_results:
        reminders_len = 0
    else:
        reminders_len = reminders_results[-1][0]
    #
    if message.text == 'cancel' or message.text == '/cancel':
        pass
    else:
        new_reminder = [x[1:-1] for x in user_results[3].split(', ')]
        new_reminder[0] = reminders_len + 1
        new_reminder[5] = message.text
        cur.execute("INSERT INTO reminders VALUES(?, ?, ?, ?, ?, ?, ?);", tuple(new_reminder))
        conn.commit()
    #
    await message.delete()
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 2,
                                text=lang[user_results[1]]['successfully'])
    await SetReminder.first()


def register_handlers_set_reminder(dp: Dispatcher):
    dp.register_message_handler(cmd_set_reminder, commands="set_reminder", state="*")
    dp.register_message_handler(time_enter, state=SetReminder.waiting_for_time)
    dp.register_callback_query_handler(days_choose, state=SetReminder.waiting_for_days)
    dp.register_message_handler(text_enter, state=SetReminder.waiting_for_text)
