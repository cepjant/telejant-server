""" Запуск сервера и клиента телеграм """

import aiohttp
from aiohttp import web
from pathlib import Path

from middlewares import allowed_hosts_middleware
from routes import routes


async def on_shutdown(application):
    """ Обработчик останова сервера """
    await application['session'].close()


async def on_startup(application):
    # проверяем что директория для хранения телеграм сессий создана или создаем ее
    Path("telegram/sessions").mkdir(exist_ok=True)

    # сессия для связи с посредником
    session = aiohttp.ClientSession()
    application['session'] = app.get('session', session)

    application.add_routes(routes)
    application.on_shutdown.append(on_shutdown)


if __name__ == '__main__':
    app = web.Application(middlewares=[allowed_hosts_middleware, ])
    app.on_startup.append(on_startup)
    web.run_app(app)
