import asyncio

from aiohttp import web
from telegram.client import telegram_client, send_telegram_message

# событийный цикл, в который будет добавлен и сервер, и клиент телеграма
loop = asyncio.get_event_loop()


async def post_send_message(request):
    """ POST запрос на отправку сообщений """

    json_data = await request.json()
    username = json_data['username']
    text = json_data['text']
    await send_telegram_message(username, text)

    return web.json_response(data={'status': 'ok'})

app = web.Application()
app.add_routes([
    web.post('/send_message/', post_send_message)
])

if __name__ == '__main__':
    telegram_client.start()
    web.run_app(app, loop=loop)
    loop.create_task(telegram_client.run_until_disconnected())

