from subprocess import call

from fastapi import APIRouter

from telegram.config import TOKEN_UPDATE, USER_PASSWORD

app_update = APIRouter()


@app_update.get('/actions/update_app', include_in_schema=False)
async def update(token: str):
    if token == TOKEN_UPDATE:
        call(f'echo {USER_PASSWORD} | sudo -S bash update', shell=True)
