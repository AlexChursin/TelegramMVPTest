from ..bot_entity import InlineViewButton
from ..button import ButtonCollection, MyButton


def get_hello_keyboard(text_config):
    now_b = MyButton(label=text_config.buttons.start_button_now.label,
                     data=text_config.buttons.start_button_now.key,
                     type_value=ButtonCollection.start_button.value)
    tomorrow_b = MyButton(label=text_config.buttons.start_button_tomorrow.label,
                          data=text_config.buttons.start_button_tomorrow.key,
                          type_value=ButtonCollection.start_button.value)
    emergency_b = MyButton(label=text_config.buttons.start_button_emergency.label,
                           data=text_config.buttons.start_button_emergency.key,
                           type_value=ButtonCollection.start_emergency_button.value)
    buttons = [
        InlineViewButton(text=now_b.label, callback=now_b.to_callback()),
        InlineViewButton(text=tomorrow_b.label, callback=tomorrow_b.to_callback()),
        InlineViewButton(text=emergency_b.label, callback=emergency_b.to_callback()),
    ]
    return buttons

