import sqlite3

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.config_reader import load_config
from app.localization import lang

config = load_config("config/bot.ini")
conn = sqlite3.connect(config.bot.way)
cur = conn.cursor()


class Lang(StatesGroup):
    start = State()
    waiting_for_lang_choose = State()


async def cmd_lang(message: types.Message):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % message.chat.id)
    user_results = cur.fetchone()
    keyboard = types.InlineKeyboardMarkup()
    lang_keys = list(lang.keys())
    #
    for x in range(0, len(lang)):
        bth = types.InlineKeyboardButton(text=lang[lang_keys[x]]['name'], callback_data=lang_keys[x])
        keyboard.add(bth)
    keyboard.add(types.InlineKeyboardButton(text='◀️' + lang[user_results[1]]['cancel'], callback_data='cancel'))
    #
    await message.delete()
    await message.answer(lang[user_results[1]]['lang_choose'], reply_markup=keyboard)
    await Lang.waiting_for_lang_choose.set()


async def lang_choose(call: types.CallbackQuery):
    cur.execute("SELECT * FROM users WHERE user_chat_id = %s" % call.message.chat.id)
    user_results = cur.fetchone()
    #
    if call.data == 'cancel' and call.data == '/cancel':
        await call.message.edit_text(text=(lang[user_results[1]]['successfully']))
    else:
        await call.message.edit_text(text=(lang[user_results[1]]['lang_chosen'] + ' <code>' +
                                           lang[call.data]['name'] + '</code>'),
                                     parse_mode=types.ParseMode.HTML)
        #
        cur.execute('UPDATE users SET lang = ? WHERE user_chat_id = ?', (call.data, call.message.chat.id))
        conn.commit()
    await call.answer()


def register_handlers_lang(dp: Dispatcher):
    dp.register_message_handler(cmd_lang, commands="lang", state="*")
    dp.register_callback_query_handler(lang_choose, state=Lang.waiting_for_lang_choose)
