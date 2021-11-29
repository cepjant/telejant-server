""" Функции-обработчики запросов на сервер """

from aiohttp import web

from telegram.client import send_telegram_message


async def send_message(request):
    """ POST запрос на отправку сообщения """

    json_data = await request.json()
    user = json_data['user']
    text = json_data['text']
    result = await send_telegram_message(user, text)
    if result:
        response = {"status": 201, "data": {"id": result.id}}
    else:
        response = {"status": 500}
    return web.json_response(**response)
