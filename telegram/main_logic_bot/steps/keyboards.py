from typing import List
from ..bot_entity import InlineViewButton, Schedule
from ..button import ButtonCollection, MyButton
from ..client_repo.client_entity import Client
from ..config.text_config import TextBot


def get_hello_keyboard(text_config: TextBot, show_ember: bool, days: List[str]):
    buttons = []
    if '2day' in days:
        buttons.append(MyButton(label=text_config.buttons.start_button_now.label, data='2day',
                                type_value=ButtonCollection.start_b.value))
    if '2morrow' in days:
        buttons.append(MyButton(label=text_config.buttons.start_button_tomorrow.label, data='2morrow',
                                type_value=ButtonCollection.start_b.value))
    if show_ember:
        buttons.append(MyButton(label=text_config.buttons.start_button_emergency.label, data='em',
                                type_value=ButtonCollection.start_emer_b.value))
    keyboard = [InlineViewButton(text=b.label, callback=b.to_callback()) for b in buttons]
    return keyboard


def get_change_time_cons_keyboard():
    callback_back_b = MyButton(label='back', data='back', type_value=ButtonCollection.back_main.value).to_callback()
    buttons = [InlineViewButton(text="Изменить время консультации", callback=callback_back_b)]
    return buttons


def get_start_button(list_times: List[Schedule]):
    return [InlineViewButton(text=str(value.time),
                             callback=MyButton(label=value.time, data=str(value.id),
                                               type_value=ButtonCollection.time_button.value).to_callback()) for
            value in list_times]

