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
    tg_client = TELEGRAM_CLIENTS[tg_client_identifier]

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

    return web.json_response(**response)


async def start_new_session(request):
    """ Принимает запрос на создание новой сессии """
    import asyncio
    from settings import API_ID, API_HASH, CLIENTS
    from telethon import TelegramClient

    from telegram.client import serve_client

    new_loop = asyncio.new_event_loop()

    def get_passcode():
        print('getting passcode')
        return '123121'

    json_data = await request.json()

    tg_client_identifier = str(json_data['tg_client_identifier'])
    telegram_client = TelegramClient(tg_client_identifier, int(API_ID), API_HASH)

    phone_number = json_data['phone_number']
    outer_service_url = json_data['endpoint_url']

    print("Инициализация клиента '%s'" % phone_number)

    # identifier - уникальное значение клиента, для которого запускается клиент телеграма
    setattr(telegram_client, 'identifier', tg_client_identifier)


    # client['identifier'] -- номер телефоне, code_callback - функция, которая вернет passcode
    # telegram_client.start(phone_number, code_callback=None)
    await new_loop.run_in_executor(None, telegram_client.start, phone_number)
    print("Телеграм клиент '%s' запущен" % phone_number)
    new_loop.create_task(serve_client(telegram_client))

