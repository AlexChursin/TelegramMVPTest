import uvicorn
from fastapi import FastAPI
from loguru import logger
from db.core import database, engine, metadata
from routes.message_route import message_route
from routes.tg_route import set_webhook, tg_route

app = FastAPI()
app.state.database = database
app.include_router(tg_route)
app.include_router(message_route, tags=["Message"])


@app.on_event("startup")
async def startup():
    url = await set_webhook()
    logger.info(f'telegram webhook url: {url}')

    metadata.create_all(engine)
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, debug=True)
