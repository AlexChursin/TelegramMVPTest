from typing import List
from ..bot_entity import InlineViewButton, Schedule, ViewButton
from ..button import ButtonCollection, MyButton
from ..client_repo.client_entity import Client
from ..config.text_config import TextBot


def get_hello_keyboard(text_config: TextBot, show_ember: bool, days: List[str]):
    buttons = []
    if '2day' in days:
        buttons.append(MyButton(label=text_config.buttons.start_button_now, data='2day',
                                type_value=ButtonCollection.start_b.value))
    if '2morrow' in days:
        buttons.append(MyButton(label=text_config.buttons.start_button_tomorrow, data='2morrow',
                                type_value=ButtonCollection.start_b.value))
    if show_ember:
        buttons.append(MyButton(label=text_config.buttons.start_button_emergency, data='em',
                                type_value=ButtonCollection.start_emer_b.value))
    keyboard = [InlineViewButton(text=b.label, callback=b.to_callback()) for b in buttons]
    return keyboard


def get_change_time_cons_keyboard(label: str):
    callback_back_b = MyButton(label='back', data='back', type_value=ButtonCollection.back_main.value).to_callback()
    buttons = [InlineViewButton(text=label, callback=callback_back_b)]
    return buttons


def get_finish_cons_buttons(label: str):
    buttons = [ViewButton(text=label)]
    return buttons



def get_time_buttons(list_times: List[Schedule]):
    buttons = [InlineViewButton(text=str(value.time),
                                callback=MyButton(label=value.time, data=str(value.id),
                                                  type_value=ButtonCollection.time_button.value).to_callback()) for
               value in list_times]
    buttons.append(InlineViewButton(text='Назад', callback=MyButton(label='menu', data='b',
                                                                    type_value=ButtonCollection.back_time_to_main.value).to_callback()))
    return buttons


def get_finish_buttons():
    buttons = [InlineViewButton(
        MyButton(label='Рекомендуем', data='r', type_value=ButtonCollection.recommend_friends.value).to_callback(),
        text='Рекомендуем друзьям'),
               InlineViewButton(
                   MyButton(label='Новый', data='new', type_value=ButtonCollection.new_query.value).to_callback(),
                   text='Новый запрос')]
    return buttons
