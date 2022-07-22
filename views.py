""" Функции-обработчики запросов на сервер """

import base64

from aiohttp import web
from telethon.tl.types import DocumentAttributeFilename

from telegram.client import send_telegram_message, TELEGRAM_CLIENTS
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
                "peer_id": result.peer_id.user_id
            }
            response = {"status": 201, "data": data}
        else:
            response = {"status": 500}
    except PeerNotFoundError:
        # пользователь для отправки сообщения не найден
        response = {"status": 400, "data": {"error": "PeerNotFound"}}

    return web.json_response(**response)
