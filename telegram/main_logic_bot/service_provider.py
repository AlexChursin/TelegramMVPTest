from messenger_api import mess_api
from .service import BotService

from .client_repo.client_provider import APIClientRepo
from ..aiogram_view import TelegramView


bot_service = BotService(view=TelegramView(),
                             text_config=mess_api.get_config_texts(),
                             client_repo=APIClientRepo())
