""" Запуск сервера и клиента телеграм """

import asyncio
import aiohttp
from aiohttp import web

from settings import CLIENTS
from middlewares import allowed_hosts_middleware
from routes import routes
from telegram.client import TELEGRAM_CLIENTS, client_handler

app = web.Application(middlewares=[allowed_hosts_middleware, ])


async def on_shutdown(application):
    """ Обработчик останова сервера """
    for session in application['sessions']:
        await session.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)

    # for identifier, telegram_client in TELEGRAM_CLIENTS.items():
    #     client = next(c for c in CLIENTS if c['identifier'] == identifier)
    #     print("Инициализация клиента '%s'" % client['label'])
    #
    #     # identifier - уникальное значение клиента, для которого запускается клиент телеграма
    #     setattr(telegram_client, 'identifier', identifier)
    #
    #     # client['identifier'] -- номер телефоне, code_callback - функция, которая вернет passcode
    #     telegram_client.start(client['identifier'], code_callback=get_passcode)
    #     print("Телеграм клиент '%s' запущен" % client['label'])
    #     loop.run_until_complete(main(telegram_client))

    web.run_app(app, loop=loop)
