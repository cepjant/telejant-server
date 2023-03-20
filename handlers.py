""" Функции-обработчики запросов на web сервер """

import base64

from aiohttp import web
from telethon.tl.types import DocumentAttributeFilename

from telegram.client import send_telegram_message, get_peer_info, start_new_session
from telegram.exceptions import PeerNotFoundError


async def send_message_handler(request):
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


async def start_new_session_handler(request):
    """ Принимает запрос на создание новой сессии """

    json_data = await request.json()

    # ключ для получения кода подтверждения
    passcode_access_key = str(json_data['passcode_access_key'])

    phone_number = json_data['phone_number']
    tg_client_identifier = json_data['tg_client_identifier']

    await start_new_session(app=request.app, tg_client_identifier=tg_client_identifier,
                            phone_number=phone_number, passcode_access_key=passcode_access_key)


async def get_telegram_client_status(request):
    """ Возвращает статус клиента телеграм, GUID которого передан в GET параметре
        telegram_guid """

    telegram_guid = request.rel_url.query['telegram_guid']

    app_telegram_clients = getattr(request.app, 'telegram_clients', {})

    if app_telegram_clients.get(telegram_guid):
        telegram_client = app_telegram_clients[telegram_guid]
        telegram_client_status = 'Connected' if await telegram_client.get_me() else 'Disconnected'
        response = {"status": 200, "data": {"telegram_client_status": telegram_client_status}}
    else:
        response = {"status": 200, "data": {"telegram_client_status": 'NotFound'}}
    return web.json_response(**response)
