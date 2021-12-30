import json

import pytest
from telegram.main_logic_bot.button import MyButton, ButtonCollection
from telegram.main_logic_bot.client_repo.client_provider import APIClientRepo
from telegram.main_logic_bot.config.text_config import TextBot
from telegram.main_logic_bot.service import BotService
from tests.view import TestView, Answers

doc_token = '9076fd887d83d240cb648e13b5d191f1'


@pytest.mark.asyncio
async def test_old_user():
    bot_service = BotService(view=TestView(),
                             text_config=TextBot(**json.load(
                                 open('../telegram/main_logic_bot/config/bot_text_word.json', 'r', encoding='UTF-8'))),
                             client_repo=APIClientRepo())
    user_id, chat_id = 0, 0
    await bot_service.answer_on_start_command(chat_id, user_id, f'start doc_{doc_token}')
    assert 'Здравствуйте, это ассистен' in Answers.last
    b = MyButton(label='выбрал завтра', data='2morrow', type_value=ButtonCollection.start_b.value)
    await bot_service.answer_callback(chat_id, chat_id, user_id, b.to_callback())
    assert 'Выберите время консультации на' in Answers.last
    callback = MyButton(label='выбрал время', data='1', type_value=ButtonCollection.time_button.value).to_callback()
    await bot_service.answer_callback(chat_id, chat_id, user_id, callback)
    assert 'акова причина вашего обращения' in Answers.last
