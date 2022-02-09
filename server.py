""" Запуск сервера и клиента телеграм """

import asyncio
import aiohttp
from aiohttp import web
from telethon import events

from routes import routes
from settings import TARGET_SYSTEM_URL
from telegram.client import telegram_client, client_handler

app = web.Application()


async def on_shutdown(application):
    """ Обработчик останова сервера """
    await application['session'].close()


async def main():
    """ Установка соединения с сервисом посредником и объявление обработчиков событий
     из телеграма """

    session = aiohttp.ClientSession()
    app['session'] = session  # app должен хранить сессию, чтобы при останове app закрыть сессию

    @telegram_client.on(events.NewMessage())
    async def income_handler(event):
        message_data = await client_handler(event)
        if message_data and TARGET_SYSTEM_URL:
            await session.post(TARGET_SYSTEM_URL, json=message_data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)

    loop.run_until_complete(main())
    telegram_client.start()
    web.run_app(app, loop=loop)
