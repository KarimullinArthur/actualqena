from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram import types
from aiogram.dispatcher.filters import Text

from loader import db, bot
from markups import keyboards
from filters.sponsors import Sponsor
from states.client.main_menu import ClientMain
from utils.datetime import get_datetime
from middleware.check_subs import check_subs as _check_subs
from middleware.trustat import get_form


async def start(message: types.Message, state: FSMContext):
    start_command = message.text
    ref_link = str(start_command[7:])
    if not db.user_exists(message.from_user.id):
        if ref_link in (db.get_ref_links() + [str(x) for x in db.get_all_link()]):
            db.add_user(message.from_user.id, ref_link,
                        get_datetime())
            if int(ref_link) in db.get_all_link():
                admins_id = db.get_admins_tg_id()
                admins_id.append(int(ref_link))
                for tg_id in admins_id:
                    if tg_id == int(ref_link):
                        msg = f"Вашим прайсом заинтересовался @{message.from_user.username}"
                    else:
                        msg = f"Прайсом {db.get_link(ref_link)['name']} заинтересовался @{message.from_user.username}"
                    await bot.send_message(tg_id, msg,
                                           disable_web_page_preview=True)

                await message.answer(await get_form(ref_link))

        else:
            db.add_user(message.from_user.id, '',
                        get_datetime())
    else:
        db.set_user_activity(message.from_user.id, True)

    if await _check_subs(message):
        if ref_link in (db.get_ref_links() + [str(x) for x in db.get_all_link()]):
            await message.answer(await get_form(ref_link), disable_web_page_preview=True)
        msg = db.get_text('welcome')
        await bot.copy_message(message.chat.id,
                               msg['chat_id'], msg['message_id'],
                               reply_markup=keyboards.main_menu(
                                   message.chat.id))
        await ClientMain.main_menu.set()


async def check_subs(callback: types.callback_query, state: FSMContext):
    if await _check_subs(callback.message):
        msg = db.get_text('welcome')
        await bot.copy_message(callback.message.chat.id,
                               msg['chat_id'], msg['message_id'],
                               reply_markup=keyboards.main_menu(
                                   callback.message.chat.id))
        await ClientMain.main_menu.set()


def register_client_main_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands='start', state='*',
                                chat_type='private')

    dp.register_callback_query_handler(check_subs, text='check_subs',
                                       state='*', chat_type='private')
