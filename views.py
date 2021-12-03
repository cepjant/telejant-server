""" Функции-обработчики запросов на сервер """

import base64

from aiohttp import web
from telethon.tl.types import DocumentAttributeFilename

from telegram.client import send_telegram_message


async def send_message(request):
    """ POST запрос на отправку сообщения """

    json_data = await request.json()
    user = json_data['user']
    text = json_data['text']
    file = None
    attributes = []

    media_content = json_data.get('media_content')
    if media_content:
        file = base64.b64decode(media_content)
        filename = DocumentAttributeFilename(json_data.get('file_name'))
        attributes.append(filename)

    result = await send_telegram_message(user, text, file=file, attributes=attributes)
    if result:
        response = {"status": 201, "data": {"id": result.id}}
    else:
        response = {"status": 500}
    return web.json_response(**response)
