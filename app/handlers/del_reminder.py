import sqlite3

from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.config_reader import load_config
from app.localization import lang

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()
bot = Bot(token=config.bot.TOKEN)


class DelReminder(StatesGroup):
    start = State()
    waiting_for_reminder = State()


async def cmd_del_reminder(message: types.Message):
    await message.delete()
    #
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    user_results = cur.fetchone()
    cur.execute("SELECT * FROM reminders WHERE user_chat_id = %s" % message.chat.id)
    reminders_results = cur.fetchall()
    local = lang[user_results[1]]
    #
    if reminders_results:
        keyboard_cancel = types.InlineKeyboardMarkup(row_width=2)
        keyboard_cancel.add(types.InlineKeyboardButton(text='◀️' + lang[user_results[1]]['cancel'],
                                                       callback_data='cancel'))
        await message.answer(lang[user_results[1]]['del_reminder'], reply_markup=keyboard_cancel)
        #
        for x in range(len(reminders_results)):
            keyboard_delete = types.InlineKeyboardMarkup(row_width=2)
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
            keyboard_delete.add(types.InlineKeyboardButton(text='🗑' + lang[user_results[1]]['delete_this'],
                                                           callback_data=str(x)))
            await message.answer(text, parse_mode=types.ParseMode.HTML, reply_markup=keyboard_delete)
            #
        await DelReminder.waiting_for_reminder.set()
    else:
        await message.answer(lang[user_results[1]]['None'])


async def reminder_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % call.message.chat.id)
    user_results = cur.fetchone()
    cur.execute('SELECT * FROM reminders WHERE user_chat_id = %s' % call.message.chat.id)
    reminders_results = cur.fetchall()
    #
    if call.data != 'cancel':
        cur.execute('DELETE FROM reminders WHERE id = %s' % int(reminders_results[int(call.data)][0]))
        conn.commit()
        await call.message.edit_text(lang[user_results[1]]['del_successfully'] % str(int(call.data) + 1))
        #
        for x in range(len(reminders_results) - int(call.data) - 1):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + x + 1)
        #
        for x in range(int(call.data) + 1):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - x - 1)
    else:
        await call.message.edit_text(lang[user_results[1]]['successfully'])
        #
        for x in range(len(reminders_results)):
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + x + 1)
    #
    await DelReminder.first()
    await call.answer()


def register_handlers_del_reminder(dp: Dispatcher):
    dp.register_message_handler(cmd_del_reminder, commands="del_reminder", state="*")
    dp.register_callback_query_handler(reminder_choose, state=DelReminder.waiting_for_reminder)
