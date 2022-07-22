from aiohttp.web import middleware

from settings import ALLOWED_HOSTS


@middleware
async def allowed_hosts_middleware(request, handler):
    """ Проверка на адрес отправителя запроса """
    host, _ = request.transport.get_extra_info('peername')
    if host in ALLOWED_HOSTS:
        resp = await handler(request)
        return resp
    else:
        raise RuntimeError('Адрес', host, 'не добавлен в ALLOWED_HOSTS')
