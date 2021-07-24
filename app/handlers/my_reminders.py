import sqlite3

from aiogram import Dispatcher, types

from app.config_reader import load_config
from app.localization import lang

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()


async def cmd_my_reminders(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    user_results = cur.fetchone()
    cur.execute("SELECT * FROM reminders WHERE user_chat_id = %s" % message.chat.id)
    reminders_results = cur.fetchall()
    local = lang[user_results[1]]
    #
    await message.delete()
    #
    if reminders_results:
        await message.answer(lang[user_results[1]]['yours_reminders'])
        #
        for x in range(0, len(reminders_results)):
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
            await message.answer(text, parse_mode=types.ParseMode.HTML)
    else:
        await message.answer(lang[user_results[1]]['None'])


def register_handlers_my_reminders(dp: Dispatcher):
    dp.register_message_handler(cmd_my_reminders, commands="my_reminders", state='*')
