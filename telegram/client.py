""" Клиент телеграм - получение и отправка сообщений """

from pathlib import Path
import phonenumbers
import random
import requests
from telethon import functions, types, TelegramClient

import settings
from telegram.exceptions import PeerNotFoundError
from telegram.handlers import new_message_handler


async def send_telegram_message(user, text, tg_client, file=None, attributes=None):
    """ Отправка сообщений """
    if user.get('user_id'):
        identifier = int(user.get('user_id'))
    elif user.get('username'):
        identifier = user.get('username')
    elif user.get('phone_number'):
        phone_number = user.get('phone_number')
        # приводим номер телефона к международному формату +7**********
        identifier = phonenumbers.format_number(
            phonenumbers.parse(phone_number, 'RU'), phonenumbers.PhoneNumberFormat.E164)
        # необходимо добавить собеседника в контакты, чтобы написать
        await add_contact(identifier, tg_client)
    else:
        return None

    peer = await get_peer(identifier, tg_client)
    return await tg_client.send_message(peer, text, file=file, attributes=attributes)


async def add_contact(phone_number: str, tg_client):
    """ При отправке пользователю по номеру телефона предварительно нужно добавить его в
        контакты """
    await tg_client(functions.contacts.ImportContactsRequest(
        contacts=[types.InputPhoneContact(
            client_id=random.randrange(-2 ** 63, 2 ** 63),
            phone=phone_number,
            first_name='',
            last_name=''
        )]
    ))


async def get_peer(identifier, tg_client):
    """ Получение пользователя для отправки сообщения. """

    # This part is IMPORTANT, because it fills the entity cache.
    await tg_client.get_dialogs()

    try:
        peer = await tg_client.get_entity(identifier)
    except ValueError:
        raise PeerNotFoundError()
    return peer


async def get_peer_info(peer_id, tg_client) -> dict:
    """ Получение информации о собеседнике
        @param peer_id: собеседник
        @param tg_client:
    """

    peer_fields = ['id', 'bot', 'first_name', 'last_name', 'phone', 'username']

    try:
        peer_entity = await tg_client.get_entity(peer_id)
    except ValueError:
        # не удалось получить пользователя
        peer_info = {'id': peer_id}
    else:
        peer_info = {field: getattr(peer_entity, field) for field in peer_fields}
    return peer_info


async def add_client_handlers(running_tg_client, app):
    """ Объявление обработчиков событий из телеграма """

    from telethon import events

    @running_tg_client.on(events.NewMessage(incoming=True))
    async def income_handler(event):
        message_data = await new_message_handler(event, tg_client=running_tg_client)

        if message_data:
            outer_service_url = getattr(running_tg_client, 'outer_service_url')

            tg_client_identifier = getattr(running_tg_client, 'tg_client_identifier')
            message_data.update({'tg_client_identifier': tg_client_identifier})

            if message_data:
                print(message_data)
                await app['session'].post(outer_service_url, json=message_data)


async def start_new_session(app, tg_client_identifier, phone_number):
    """ Запускает новую сессиию телеграм 
    
        @param app: Экземпляр запущенного приложения aiohttp.web.Application
        
    """ 

    outer_service_url = settings.TARGET_SYSTEM_URL

    session_filename = tg_client_identifier + '_' + phone_number
    telegram_client = TelegramClient(
        str(Path("telegram/sessions/" + session_filename)),
        int(settings.API_ID), settings.API_HASH)

    # вешаем на ТГ клиент необходимые данные для связи с внешним сервисом
    setattr(telegram_client, 'outer_service_url', outer_service_url)
    setattr(telegram_client, 'tg_client_identifier', tg_client_identifier)

    # в приложение веб сервера добавляем созданный ТГ клиент
    app_telegram_clients = getattr(app, 'telegram_clients', {})

    if app_telegram_clients.get(tg_client_identifier):
        response = {"status": 400, "data": {"error": "TelegramClientIsAlreadyRunning"}}
        return web.json_response(**response)

    app_telegram_clients[tg_client_identifier] = telegram_client
    setattr(app, 'telegram_clients', app_telegram_clients)

    print("Инициализация клиента '%s'" % phone_number)

    received_passcodes = []

    def get_passcode():
        """ Получение кода подтверждения для создания сессии """
        import time

        while True:
            url = outer_service_url
            response = requests.post(url, json={"required": "passcode",
                                                "access_key": passcode_access_key})
            time.sleep(3)

            if response.ok and response.text != 'null':
                passcode = response.text
                if passcode not in received_passcodes:
                    # если мы уже пробовали этот passcode и он неверный -> ожидаем другой
                    received_passcodes.append(passcode)
                    return response.text

    await telegram_client.start(phone_number, code_callback=get_passcode)
    print("Телеграм клиент '%s' запущен" % phone_number)

    loop = asyncio.get_event_loop()
    loop.create_task(add_client_handlers(telegram_client, app=app))