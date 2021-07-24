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


class EditReminder(StatesGroup):
    start = State()
    waiting_for_reminder = State()
    waiting_for_edit_type = State()
    editing_time = State()
    editing_days = State()
    editing_text = State()


async def cmd_edit_reminder(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    user_results = cur.fetchone()
    cur.execute('SELECT * FROM reminders WHERE user_chat_id = %s' % message.chat.id)
    reminders_results = cur.fetchall()
    local = lang[user_results[1]]
    #
    await message.delete()
    #
    if reminders_results:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text='◀️' + lang[user_results[1]]['cancel'], callback_data='cancel'))
        await message.answer(lang[user_results[1]]['edit_reminder'], reply_markup=keyboard)
        #
        for x in range(len(reminders_results)):
            keyboard_edit = types.InlineKeyboardMarkup(row_width=2)
            #
            time = local['Time'] + ': ' + reminders_results[x][2]
            #
            days = local['Days'] + ':'
            if reminders_results[x][3] != 'onetime':
                days_list = reminders_results[x][3].split('|')
                for y in range(len(days_list)):
                    if days_list[y] == '1':
                        if days != local['Days'] + ':':
                            days += ','
                        days += ' ' + local['week%s' % y]
            else:
                days += ' ' + local['onetime']
            #
            if len(reminders_results[x][5]) > 50:
                reminder_text = reminders_results[x][5][0:50] + '...'
            else:
                reminder_text = reminders_results[x][5]
            #
            text = '<code>' + str(x + 1) + ')' + '</code>' + '\n' + time + '\n' + days + '\n' + \
                   local['Text'] + ': ' + reminder_text
            #
            keyboard_edit.add(types.InlineKeyboardButton(text='✏️' + lang[user_results[1]]['edit_this'],
                                                         callback_data=str(x)))
            await message.answer(text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard_edit)
        #
        await EditReminder.waiting_for_reminder.set()
    #
    else:
        await message.answer(lang[user_results[1]]['None'])


async def reminder_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % call.message.chat.id)
    user_results = cur.fetchone()
    cur.execute('SELECT * FROM reminders WHERE user_chat_id = %s' % call.message.chat.id)
    reminders_results = cur.fetchall()
    #
    if call.data != 'cancel':
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(types.InlineKeyboardButton(text='🕔' + lang[user_results[1]]['Time'], callback_data='time'),
                     types.InlineKeyboardButton(text='☀️' + lang[user_results[1]]['Days'], callback_data='days'),
                     types.InlineKeyboardButton(text='💬' + lang[user_results[1]]['Text'], callback_data='text'),
                     types.InlineKeyboardButton(text='◀️' + lang[user_results[1]]['cancel'], callback_data='cancel'))
        #
        for x in range(len(reminders_results) - int(call.data) - 1):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + x + 1)
        for x in range(int(call.data) + 1):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - x - 1)
        #
        cur.execute('UPDATE users SET reminder_id = ? WHERE user_chat_id = ?;',
                    (reminders_results[int(call.data)][0], call.message.chat.id))
        conn.commit()
        #
        await call.message.edit_text(lang[user_results[1]]['edit_reminder_type'] % str(int(call.data) + 1),
                                     reply_markup=keyboard)
        await EditReminder.next()
    #
    else:
        await call.message.edit_text(lang[user_results[1]]['successfully'])
        for x in range(len(reminders_results)):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + x + 1)
        #
        await EditReminder.first()
    #
    await call.answer()


async def edit_type_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % call.message.chat.id)
    user_results = cur.fetchone()
    #
    if call.data == 'time':
        message = await call.message.edit_text(lang[user_results[1]]['new_time_enter'])
        cur.execute('UPDATE users SET message_id = ? WHERE user_chat_id = ?;',
                    (message.message_id, call.message.chat.id))
        conn.commit()
        await EditReminder.editing_time.set()
    #
    elif call.data == 'days':
        cur.execute("SELECT * FROM reminders WHERE id = %s;" % user_results[4])
        reminder_results = cur.fetchone()
        #
        keyboard_results = ['❌', '❌', '❌', '❌', '❌', '❌', '❌']
        if reminder_results[3] != 'onetime':
            local_days = reminder_results[3].split('|')
            for x in range(7):
                if int(local_days[x]) == 1:
                    keyboard_results[x] = '✅'

            #
            cur.execute(
                "UPDATE keyboard SET Monday = ?, Tuesday = ?, Wednesday = ?, Thursday = ?, Friday = ?, Saturday = ?, "
                "Sunday = ? WHERE user_chat_id = ?;", (*keyboard_results, call.message.chat.id))
            conn.commit()
        #
        keyboard_results = [call.message.chat.id, *keyboard_results]
        #
        await call.message.edit_text(text=lang[user_results[1]]['choose_days'],
                                     reply_markup=DAYS_keyboard(keyboard_results, lang[user_results[1]]))
        await EditReminder.editing_days.set()
    #
    elif call.data == 'text':
        message = await call.message.edit_text(lang[user_results[1]]['new_text_enter'])
        cur.execute('UPDATE users SET message_id = ? WHERE user_chat_id = ?;',
                    (message.message_id, call.message.chat.id))
        conn.commit()
        await EditReminder.editing_text.set()
    #
    elif call.data == 'cancel':
        await call.message.edit_text(lang[user_results[1]]['successfully'])
        await EditReminder.first()
    #
    await call.answer()


async def edit_time(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % message.chat.id)
    user_results = cur.fetchone()
    cur.execute("SELECT * FROM reminders WHERE id = %s;" % user_results[4])
    reminder_results = cur.fetchone()
    local = lang[user_results[1]]
    #
    await message.delete()
    #
    try:
        if len(message.text) == 5 and int(message.text[0]) < 3 and int(message.text[1]) < 10 and \
                message.text[2] == ':' and int(message.text[3]) < 6 and int(message.text[4]) < 10 and \
                int(message.text[0:2]) < 24:
            days = [False, False, False, False, False, False, False]
            for y in range(0, 7):
                if reminder_results[3][y] == '1':
                    days[y] = True
                else:
                    days[y] = False
            #
            local_time = message.text
            #
            time, local_days, days_ = time_operation(message.text, user_results[2], *days)
            if reminder_results[3] == 'onetime':
                days_ = 'onetime'
            #
            cur.execute("UPDATE reminders SET time = ?, local_time = ?, days = ? WHERE id = ?",
                        (time, local_time, days_, user_results[4]))
            conn.commit()
            await bot.edit_message_text(chat_id=message.chat.id, message_id=user_results[5],
                                        text=local['successfully'])
        elif message.text == '/cancel' or message.text == 'cancel':
            await bot.edit_message_text(chat_id=message.chat.id, message_id=user_results[5],
                                        text=local['successfully'])
        else:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=user_results[5],
                                        text=local['time_error'])
    #
    except ValueError:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=user_results[3],
                                    text=local['time_error'])
    #
    await EditReminder.first()


async def edit_days(call: types.CallbackQuery):
    cur.execute("SELECT * FROM keyboard WHERE user_chat_id = %s;" % call.message.chat.id)
    keyboard_results = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % call.message.chat.id)
    user_results = cur.fetchone()
    cur.execute("SELECT * FROM reminders WHERE id = %s" % user_results[4])
    reminder_results = cur.fetchone()
    week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    local = lang[user_results[1]]
    #
    if call.data == 'ready':
        if keyboard_results != [call.message.chat.id, '❌', '❌', '❌', '❌', '❌', '❌', '❌']:
            days = [False, False, False, False, False, False, False]
            for x in range(0, 7):
                if keyboard_results[x + 1] == '❌':
                    days[x] = False
                else:
                    days[x] = True
            #
            time, local_days, days_ = time_operation(reminder_results[2], user_results[2], *days)
            cur.execute('UPDATE reminders SET days = ?, local_days = ?, time = ? WHERE id = %s' % user_results[4],
                        (days_, local_days, time))
            cur.execute('UPDATE keyboard SET Monday = ?, Tuesday = ?, Wednesday = ?, Thursday = ?, Friday = '
                        '?, Saturday = ?, Sunday= ? WHERE user_chat_id = %s' % call.message.chat.id,
                        ('❌', '❌', '❌', '❌', '❌', '❌', '❌'))
            conn.commit()
            #
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=local['successfully'])
            await EditReminder.next()
        else:
            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=local['days_error'],
                                            reply_markup=DAYS_keyboard(keyboard_results, local))
            except MessageNotModified:
                pass
    #
    elif call.data == '/cancel' or call.data == 'cancel':
        for v in range(0, 7):
            cur.execute("UPDATE keyboard SET %s = ? WHERE user_chat_id = ?;" % week[v], ('❌', call.message.chat.id))
        conn.commit()
        #
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=local['successfully'])
        await EditReminder.first()
    #
    elif call.data == 'onetime':
        time, local_days, days_ = time_operation(reminder_results[2], user_results[2],
                                                 False, False, False, False, False, False, False)
        cur.execute('UPDATE reminders SET days = ?, local_days = ?, time = ? WHERE id = %s' % user_results[4],
                    ('onetime', 'onetime', time))
        cur.execute('UPDATE keyboard SET Monday = ?, Tuesday = ?, Wednesday = ?, Thursday = ?, Friday = '
                    '?, Saturday = ?, Sunday= ? WHERE user_chat_id = %s' % call.message.chat.id,
                    ('❌', '❌', '❌', '❌', '❌', '❌', '❌'))
        conn.commit()
        #
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=local['successfully'])
        await EditReminder.first()
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


async def edit_text(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s;" % message.chat.id)
    user_results = cur.fetchone()
    #
    if message.text == 'cancel' or message.text == '/cancel':
        pass
    else:
        cur.execute('UPDATE reminders SET text = ? WHERE id = ?;', (message.text, user_results[4]))
        conn.commit()
    #
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=user_results[5])
    await message.answer(lang[user_results[1]]['successfully'])
    await EditReminder.first()


def register_handlers_edit_reminder(dp: Dispatcher):
    dp.register_message_handler(cmd_edit_reminder, commands="edit_reminder", state="*")
    dp.register_callback_query_handler(reminder_choose, state=EditReminder.waiting_for_reminder)
    dp.register_callback_query_handler(edit_type_choose, state=EditReminder.waiting_for_edit_type)
    dp.register_message_handler(edit_time, state=EditReminder.editing_time)
    dp.register_callback_query_handler(edit_days, state=EditReminder.editing_days)
    dp.register_message_handler(edit_text, state=EditReminder.editing_text)
