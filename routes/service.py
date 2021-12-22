from typing import Optional

from messenger_api import mess_api
from telegram.aiogram_view import tg_view
from telegram.main_logic_bot.bot_entity import InlineViewButton
from telegram.main_logic_bot.button import MyButton, ButtonCollection
from telegram.main_logic_bot.client_repo.user_bot_state import State


async def finish_consulate(dialog_id: int, text: str, doctor_name: Optional[str]) -> Optional[int]:
    consulate = await mess_api.get_consulate(dialog_id)
    buttons = [InlineViewButton(MyButton(label='Рекомендуем', data='r', type_value=ButtonCollection.recommend_friends.value).to_callback(), text='Рекомендуем друзьям'),
               InlineViewButton(MyButton(label='Новый', data='new', type_value=ButtonCollection.new_query.value).to_callback(), text='Новый запрос')]

    if consulate:
        if consulate.chat_id is not None:
            await tg_view.send_assistant_message(chat_id=consulate.chat_id, text=text, doctor_n=doctor_name, inline_buttons=buttons)

            client = await mess_api.get_client(consulate.user_id)
            client.status = State.start_first.value
            client.consulate = None
            await mess_api.update_client(client)
            return consulate.chat_id
    return None
