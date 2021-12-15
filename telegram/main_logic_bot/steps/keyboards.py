from typing import List
from ..bot_entity import InlineViewButton
from ..button import ButtonCollection, MyButton
from ..client_repo.client_entity import Client


def get_hello_keyboard(text_config, list_key_days: List[str]):
    buttons = []
    if len(list_key_days[0]):
        buttons.append(MyButton(label=text_config.buttons.start_button_now.label,
                                data=list_key_days[0],
                                type_value=ButtonCollection.start_button.value))
    if len(list_key_days[1]):
        buttons.append(MyButton(label=text_config.buttons.start_button_tomorrow.label,
                                data=list_key_days[1],
                                type_value=ButtonCollection.start_button.value))
    if len(list_key_days[2]):
        buttons.append(MyButton(label=text_config.buttons.start_button_emergency.label,
                                data=list_key_days[2],
                                type_value=ButtonCollection.start_emergency_button.value))
    keyboard = [InlineViewButton(text=b.label, callback=b.to_callback()) for b in buttons]
    return keyboard


def get_change_time_cons_keyboard():
    callback_back_b = MyButton('back', 'back', type_value=ButtonCollection.back_main.value).to_callback()
    buttons = [InlineViewButton(text="Изменить время консультации", callback=callback_back_b)]
    return buttons


def get_start_button(list_times):
    return [InlineViewButton(text=str(value.time),
                             callback=MyButton(value.time, value.id,
                                               ButtonCollection.time_button.value).to_callback()) for
            value in list_times]

