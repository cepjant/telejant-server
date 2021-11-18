""" Урлы взаимодействия с сервером """

from aiohttp import web

from views import post_send_message

routes = [
    web.post('/send_message/', post_send_message)
]
