""" Функции-обработчики запросов на сервер """

from aiohttp import web

from telegram.client import send_telegram_message


async def post_send_message(request):
    """ POST запрос на отправку сообщений """

    json_data = await request.json()
    username = json_data['username']
    text = json_data['text']
    await send_telegram_message(username, text)

    return web.json_response(data={'status': 'ok'})
