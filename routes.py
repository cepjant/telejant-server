""" Урлы взаимодействия с сервером """

from aiohttp import web

from handlers import send_message_handler, start_new_session_handler, get_telegram_client_status

routes = [
    web.post('/send_message/', send_message_handler),
    web.post('/start_client/', start_new_session_handler),
    web.get('/status/', get_telegram_client_status)
]
