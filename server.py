""" Запуск сервера и клиента телеграм """

import asyncio
import aiohttp
from aiohttp import web
from telethon import events

from routes import routes
from settings import SERVICE_URL
from telegram.client import telegram_client, client_handler


async def main():
    session = aiohttp.ClientSession()

    @telegram_client.on(events.NewMessage())
    async def income_handler(event):
        message_data = await client_handler(event)
        if message_data:
            await session.post(SERVICE_URL, json=message_data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    app = web.Application()
    app.add_routes(routes)

    loop.run_until_complete(main())
    telegram_client.start()
    web.run_app(app, loop=loop)
