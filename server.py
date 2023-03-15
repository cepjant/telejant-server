""" Запуск сервера и клиента телеграм """

import asyncio
from aiohttp import web

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

    web.run_app(app, loop=loop)
