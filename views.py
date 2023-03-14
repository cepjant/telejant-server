""" Функции-обработчики запросов на сервер """

import base64

from aiohttp import web
from telethon.tl.types import DocumentAttributeFilename

from telegram.client import send_telegram_message, TELEGRAM_CLIENTS, get_peer_info
from telegram.exceptions import PeerNotFoundError


async def send_message(request):
    """ POST запрос на отправку сообщения """

    json_data = await request.json()

    # определяем, от какого пользователя (сессии) будем отправлять сообщение
    tg_client_identifier = str(json_data['tg_client_identifier'])

    app_telegram_clients = getattr(request.app, 'telegram_clients', {})
    tg_client = app_telegram_clients.get(tg_client_identifier)

    if tg_client:
        user = json_data['user']
        text = json_data['text']
        file = None
        attributes = []

        media_content = json_data.get('media_content')
        if media_content:
            file = base64.b64decode(media_content)
            filename = DocumentAttributeFilename(json_data.get('file_name'))
            attributes.append(filename)

        try:
            result = await send_telegram_message(user, text, tg_client,
                                                 file=file, attributes=attributes)
            if result:
                data = {
                    "id": result.id,
                    "peer": await get_peer_info(result.peer_id.user_id, tg_client)
                }
                response = {"status": 201, "data": data}
            else:
                response = {"status": 500}
        except PeerNotFoundError:
            # пользователь для отправки сообщения не найден
            response = {"status": 400, "data": {"error": "PeerNotFound"}}
    else:
        # телеграм клиент, с которого нужно отправить сообщение, не найден
        response = {"status": 400, "data": {"error": "TelegramClientNotFound"}}

    print(response)
    return web.json_response(**response)


async def start_new_session(request):
    """ Принимает запрос на создание новой сессии """
    import asyncio
    from settings import API_ID, API_HASH
    from telethon import TelegramClient
    import requests
    from telegram.client import serve_client

    loop = asyncio.get_event_loop()

    json_data = await request.json()

    # ключ для получения кода подтверждения
    passcode_access_key = str(json_data['passcode_access_key'])

    phone_number = json_data['phone_number']
    outer_service_url = json_data['endpoint_url']
    tg_client_identifier = json_data['tg_client_identifier']

    telegram_client = TelegramClient(phone_number, int(API_ID), API_HASH)
    setattr(telegram_client, 'outer_service_url', outer_service_url)
    setattr(telegram_client, 'phone_number', phone_number)
    setattr(telegram_client, 'tg_client_identifier', tg_client_identifier)

    app_telegram_clients = getattr(request.app, 'telegram_clients', {})
    app_telegram_clients[tg_client_identifier] = telegram_client
    setattr(request.app, 'telegram_clients', app_telegram_clients)

    print("Инициализация клиента '%s'" % phone_number)

    # identifier - уникальное значение клиента, для которого запускается клиент телеграма
    # setattr(telegram_client, 'identifier', passcode_access_key)

    received_passcodes = []

    def get_passcode():
        import time

        while True:
            url = outer_service_url
            response = requests.post(url, json={"required": "passcode",
                                                "access_key": passcode_access_key})
            time.sleep(3)

            if response.ok and response.text != 'null':
                passcode = response.text
                if passcode not in received_passcodes:
                    # если мы уже пробовали этот passcode, он неверный -> ожидаем другой
                    received_passcodes.append(passcode)
                    return response.text

    await telegram_client.start(phone_number, code_callback=get_passcode)
    print("Телеграм клиент '%s' запущен" % phone_number)
    loop.create_task(serve_client(telegram_client, app=request.app))

