""" Урлы взаимодействия с сервером """

from aiohttp import web

from views import send_message

routes = [
    web.post('/send_message/', send_message)
]
