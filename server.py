""" Запуск сервера и клиента телеграм """

import asyncio
import aiohttp
from aiohttp import web

from settings import CLIENTS
from middlewares import allowed_hosts_middleware
from routes import routes
from telegram.client import TELEGRAM_CLIENTS, new_message_handler

app = web.Application(middlewares=[allowed_hosts_middleware, ])


async def on_shutdown(application):
    """ Обработчик останова сервера """
    await application['session'].close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)

    # сессия для связи с посредником
    session = aiohttp.ClientSession()
    app['session'] = app.get('session', session)

    web.run_app(app, loop=loop)
