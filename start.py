import uvicorn
from fastapi import FastAPI
from loguru import logger

from routes.hook_cd_route import app_update
from routes.message_route import message_route
from routes.tg_route import set_webhook, tg_route
from telegram.config import SERVER_PREFIX

app = FastAPI(title='API TELEGRAM BOT', description='API для взаимодействия с телеграмм ботом', version='1.0.0', docs_url=f'{SERVER_PREFIX}/swagger', openapi_url=f'{SERVER_PREFIX}/openapi.json')
app.include_router(tg_route, prefix=SERVER_PREFIX)
app.include_router(message_route, tags=["Message"], prefix=SERVER_PREFIX)
app.include_router(app_update, tags=["CI/CD"], prefix=SERVER_PREFIX)


@app.on_event("startup")
async def startup():
    url = await set_webhook()
    logger.info(f'telegram webhook url: {url}')



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081, debug=True)
