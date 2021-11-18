""" Запуск сервера и клиента телеграм """

import asyncio
from aiohttp import web

from routes import routes
from telegram.client import telegram_client

# событийный цикл, в который будет добавлен сервер и клиент телеграма
loop = asyncio.get_event_loop()

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    telegram_client.start()
    web.run_app(app, loop=loop)
    loop.create_task(telegram_client.run_until_disconnected())

