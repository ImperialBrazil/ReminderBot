import sqlite3

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.config_reader import load_config
from app.keyboards import UTC_keyboard
from app.localization import lang

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()


class Start(StatesGroup):
    start = State()
    waiting_for_time_zone = State()


async def cmd_start(message: types.Message):
    await message.delete()
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    users_results = cur.fetchone()
    locale = message.from_user.locale
    not_in = False
    #
    if locale.language not in lang:
        await message.answer(lang['en']['start'])
        lang_ = 'en'
        not_in = True
    elif users_results:
        await message.answer(lang[users_results[1]]['start'])
        lang_ = users_results[1]
    else:
        await message.answer(lang[locale.language]['start'])
        lang_ = locale.language
    #
    if not users_results:
        users_results = [message.chat.id, lang_, None, None, None, None]
        keyboard = [message.chat.id, '❌', '❌', '❌', '❌', '❌', '❌', '❌']
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);", users_results)
        cur.execute("INSERT INTO keyboard VALUES(?, ?, ?, ?, ?, ?, ?, ?);", keyboard)
        conn.commit()
        if not_in:
            await message.answer(
                lang['en']['not_in'] % ('<code>' + locale.language_name.capitalize() + '</code>'),
                reply_markup=UTC_keyboard(lang[users_results[1]], True),
                parse_mode=types.ParseMode.HTML)
        else:
            await message.answer(
                lang[lang_]['lang'] % ('<code>' + lang[lang_]['name'] + '</code>'),
                reply_markup=UTC_keyboard(lang[users_results[1]], True),
                parse_mode=types.ParseMode.HTML)
    #
    elif users_results[1] and not users_results[2]:
        await message.answer(lang[users_results[1]]['lang'] %
                             ('<code>' + lang[users_results[1]]['name'] + '</code>'),
                             reply_markup=UTC_keyboard(lang[users_results[1]], True),
                             parse_mode=types.ParseMode.HTML)
    #
    elif users_results[1] and users_results[2]:
        await message.answer(lang[users_results[1]]['lang&utc'] %
                             (('<code>' + lang[users_results[1]]['name'] + '</code>'),
                              ('<code>' + 'UTC' + users_results[2] + '</code>')),
                             parse_mode=types.ParseMode.HTML)
    #
    conn.commit()
    await Start.waiting_for_time_zone.set()


async def start_time_zone_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % call.message.chat.id)
    user_results = cur.fetchone()
    time_zone = call.data[3::]
    #
    await call.message.edit_text(lang[user_results[1]]['lang&utc'] %
                                 (('<code>' + lang[user_results[1]]['name'] + '</code>'),
                                  '<code>' + 'UTC' + call.data[3::] + '</code>'),
                                 parse_mode=types.ParseMode.HTML)
    #
    cur.execute("UPDATE users SET utc_code = ? WHERE user_chat_id = ?", (time_zone, call.message.chat.id))
    conn.commit()
    await call.answer()
    await Start.first()


async def cmd_help(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    user_results = cur.fetchone()
    #
    text = lang[user_results[1]]['help']
    commands = text.split(' | ')
    text = ''
    for x in commands:
        text += x + '\n'
    await message.delete()
    await message.answer(text)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_callback_query_handler(start_time_zone_choose, state=Start.waiting_for_time_zone)
    dp.register_message_handler(cmd_help, commands="help", state="*")
