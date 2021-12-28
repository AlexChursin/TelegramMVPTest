from .service import BotService
from ..aiogram_controller import get_config_from_url
from ..aiogram_view import tg_view

from .client_repo.client_provider import APIClientRepo

bot_service = BotService(view=tg_view,
                         text_config=get_config_from_url(),
                         client_repo=APIClientRepo())
