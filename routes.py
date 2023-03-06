""" Урлы взаимодействия с сервером """

from aiohttp import web

from views import send_message, start_new_session

routes = [
    web.post('/send_message/', send_message),
    web.post('/start_client/', start_new_session)
]
