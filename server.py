""" Запуск сервера и клиента телеграм """

import asyncio
import aiohttp
from aiohttp import web
from pathlib import Path

from middlewares import allowed_hosts_middleware
from routes import routes

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

    # проверяем что директория для хранения телеграм сессий создана или создаем ее
    Path("telegram/sessions").mkdir(exist_ok=True)

    web.run_app(app, loop=loop)
