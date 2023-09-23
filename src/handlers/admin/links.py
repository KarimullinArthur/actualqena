from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram import types
from aiogram.dispatcher.filters import Text

import config
from markups import keyboards
from loader import db
from states.admin.main_menu import AdminMain
from states.admin.links import LinksManagement, AddLinks


async def links(message: types.Message, state: FSMContext):
    await message.answer(message.text, reply_markup=keyboards.links())
    await LinksManagement.main_menu.set()


async def show_links(message: types.Message, state: FSMContext):
    await message.answer(message.text)


async def add_link(message: types.Message, state: FSMContext):
    await message.answer("Чьё ссылка? (тг йд)",
                         reply_markup=keyboards.cancel())
    await AddLinks.tg_id.set()


async def add_link_tg_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text

    await message.answer("Ссылки? (Через запятую без пробела url1,url2,url3)")

    await AddLinks.next()


async def add_link_links(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['links'] = message.text.split(',')

    await message.answer('Юзернэйм?')

    await AddLinks.next()


async def add_link_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text

    await message.answer('Имя? (В родительном падеже)')
    await AddLinks.next()


async def add_link_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer('Добавляем?', reply_markup=keyboards.check_yes_no())
    await AddLinks.next()


async def add_link_check(message: types, state: FSMContext):
    if message.text == keyboards.text_button_yes:
        async with state.proxy() as data:
            await message.answer(f'''Добавил\nВот ссылка:,
https://t.me/{config.BOT_NAME}?start={data['tg_id']}''',
                                 reply_markup=keyboards.links())
            db.add_link(data['tg_id'], data['links'], data['username'],
                        data['name'])
    else:
        await message.answer('Отменил', reply_markup=keyboards.links())

    await LinksManagement.main_menu.set()


async def del_link(message: types.Message, state: FSMContext):
    await message.answer(message.text)


def register_links(dp: Dispatcher):
    dp.register_message_handler(links, Text(keyboards.text_button_links),
                                state=AdminMain.main_menu)

    dp.register_message_handler(show_links,
                                Text(keyboards.text_button_my_links),
                                state=LinksManagement.main_menu)

    dp.register_message_handler(add_link,
                                Text(keyboards.text_button_create_link),
                                state=LinksManagement.main_menu)

    dp.register_message_handler(add_link_tg_id,
                                content_types='text',
                                state=AddLinks.tg_id)

    dp.register_message_handler(add_link_links,
                                content_types='text',
                                state=AddLinks.links)

    dp.register_message_handler(add_link_username,
                                content_types='text',
                                state=AddLinks.username)

    dp.register_message_handler(add_link_name,
                                content_types='text',
                                state=AddLinks.name)

    dp.register_message_handler(add_link_check,
                                content_types='text',
                                state=AddLinks.check)

    dp.register_message_handler(del_link,
                                Text(keyboards.text_button_delete_link),
                                state=LinksManagement.main_menu)
