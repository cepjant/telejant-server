""" Урлы взаимодействия с сервером """

from aiohttp import web

from handlers import send_message, start_new_session, get_telegram_client_status

routes = [
    web.post('/send_message/', send_message),
    web.post('/start_client/', start_new_session),
    web.get('/status/', get_telegram_client_status)
]
