from aiogram.dispatcher.filters.state import StatesGroup, State


class LinksManagement(StatesGroup):
    main_menu = State()


class AddLinks(StatesGroup):
    tg_id = State()
    links = State()
    username = State()
    name = State()

    check = State()


class DelLink(StatesGroup):
    tg_id = State()
