""" Запуск сервера и клиента телеграм """

import asyncio
import aiohttp
from aiohttp import web
from telethon import events

from settings import CLIENTS
from middlewares import allowed_hosts_middleware
from routes import routes
from telegram.client import TELEGRAM_CLIENTS, client_handler

app = web.Application(middlewares=[allowed_hosts_middleware, ])


async def on_shutdown(application):
    """ Обработчик останова сервера """
    for session in application['sessions']:
        await session.close()


async def main(running_tg_client):
    """ Установка соединения с сервисом посредником и объявление обработчиков событий
     из телеграма """

    session = aiohttp.ClientSession()
    app['sessions'] = app.get('sessions', [])
    app['sessions'].append(session)  # app должен хранить сессии, чтобы при останове app

    # закрыть сессию

    @running_tg_client.on(events.NewMessage())
    async def income_handler(event):
        message_data = await client_handler(event, tg_client=running_tg_client)

        if message_data:
            # message_data может быть None, если этот тип диалога не обрабатывается

            # получаем идентификатор клиента, для которого работает клиент телеграма
            tg_client_identifier = getattr(running_tg_client, 'identifier')
            # и передаем его вместе с запросом
            message_data.update({'tg_client_identifier': tg_client_identifier})

            # из настроек окружения берем урл клиента, на который нужно отправлять полученные
            # сообщения
            target_system_url = next(c['target_system_url'] for c in CLIENTS
                                     if c['identifier'] == tg_client_identifier)
            if message_data:
                await session.post(target_system_url, json=message_data)


async def get_password():
    # websocket?
    pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)

    for identifier, telegram_client in TELEGRAM_CLIENTS.items():
        client = next(c for c in CLIENTS if c['identifier'] == identifier)
        print("Инициализация клиента '%s'" % client['label'])

        # identifier - уникальное значение клиента, для которого запускается клиент телеграма
        setattr(telegram_client, 'identifier', identifier)
        telegram_client.start(client['phone_number'])
        print("Телеграм клиент '%s' запущен" % client['label'])
        loop.run_until_complete(main(telegram_client))

    web.run_app(app, loop=loop)
