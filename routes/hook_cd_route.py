from subprocess import call

from fastapi import APIRouter, Query

from telegram.config import TOKEN_UPDATE, USER_PASSWORD

app_update = APIRouter()


@app_update.get('/actions/update_app', description='авто деплой приложения из github')
async def update_app(token: str):
    if token == TOKEN_UPDATE:
        call(f'echo {USER_PASSWORD} | sudo -S bash update', shell=True)
