from telebot import types


def get_markup_from_buttons(button_list):
    keyboard = []
    for button in button_list:
        if button['callback_data']:
            keyboard.append(
                [types.InlineKeyboardButton(text=button['name'], callback_data=button['action_click_display'])])
    return types.InlineKeyboardMarkup(keyboard)
