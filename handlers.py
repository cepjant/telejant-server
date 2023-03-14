""" Функции-обработчики запросов на web сервер """

import base64

from aiohttp import web
import asyncio
import requests
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeFilename

from settings import API_ID, API_HASH
from telegram.client import send_telegram_message, get_peer_info, add_client_handlers
from telegram.exceptions import PeerNotFoundError


async def send_message(request):
    """ POST запрос на отправку сообщения """

    json_data = await request.json()

    # определяем, от какого пользователя (сессии) будем отправлять сообщение
    tg_client_identifier = str(json_data['tg_client_identifier'])

    # ищем, добавлен ли переданный клиент в работающее приложение
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
            message = await send_telegram_message(user, text, tg_client,
                                                  file=file, attributes=attributes)
            if message:
                data = {
                    "id": message.id,
                    "peer": await get_peer_info(message.peer_id.user_id, tg_client)
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

    return web.json_response(**response)


async def start_new_session(request):
    """ Принимает запрос на создание новой сессии """

    json_data = await request.json()

    # ключ для получения кода подтверждения
    passcode_access_key = str(json_data['passcode_access_key'])

    phone_number = json_data['phone_number']
    outer_service_url = json_data['endpoint_url']
    tg_client_identifier = json_data['tg_client_identifier']

    # вешаем на ТГ клиент необходимые данные для связи с внешним сервисом
    telegram_client = TelegramClient(phone_number, int(API_ID), API_HASH)
    setattr(telegram_client, 'outer_service_url', outer_service_url)
    setattr(telegram_client, 'tg_client_identifier', tg_client_identifier)

    # в приложение веб сервера добавляем созданный ТГ клиент
    app_telegram_clients = getattr(request.app, 'telegram_clients', {})

    if app_telegram_clients.get(tg_client_identifier):
        response = {"status": 400, "data": {"error": "TelegramClientIsAlreadyRunning"}}
        return web.json_response(**response)

    app_telegram_clients[tg_client_identifier] = telegram_client
    setattr(request.app, 'telegram_clients', app_telegram_clients)

    print("Инициализация клиента '%s'" % phone_number)

    received_passcodes = []

    def get_passcode():
        """ Получение кода подтверждения для создания сессии """
        import time

        while True:
            url = outer_service_url
            response = requests.post(url, json={"required": "passcode",
                                                "access_key": passcode_access_key})
            time.sleep(3)

            if response.ok and response.text != 'null':
                passcode = response.text
                if passcode not in received_passcodes:
                    # если мы уже пробовали этот passcode и он неверный -> ожидаем другой
                    received_passcodes.append(passcode)
                    return response.text

    await telegram_client.start(phone_number, code_callback=get_passcode)
    print("Телеграм клиент '%s' запущен" % phone_number)

    loop = asyncio.get_event_loop()
    loop.create_task(add_client_handlers(telegram_client, app=request.app))


async def get_telegram_client_status(request):
    """ Возвращает статус клиента телеграм, GUID которого передан в GET параметре
        telegram_guid """

    telegram_guid = request.rel_url.query['telegram_guid']

    app_telegram_clients = getattr(request.app, 'telegram_clients', {})

    if app_telegram_clients.get(telegram_guid):
        telegram_client = app_telegram_clients[telegram_guid]
        telegram_client_status = 'Connected' if telegram_client.is_connected() else 'Disconnected'
        response = {"status": 200, "data": {"telegram_client_status": telegram_client_status}}
    else:
        response = {"status": 200, "data": {"telegram_client_status": 'NotFound'}}
    return web.json_response(**response)
