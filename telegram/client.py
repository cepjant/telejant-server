""" Клиент телеграм - получение и отправка сообщений """

import aiohttp
import phonenumbers
import random
from telethon import TelegramClient
from telethon import functions, types

from settings import API_ID, API_HASH, CLIENTS
from telegram.exceptions import PeerNotFoundError
from telegram.handlers import private_message_handler

# пользователи телеграм, у каждого свой идентификатор и свой экземпляр клиента телеграма
# (своя сессия)
TELEGRAM_CLIENTS = {}
for client in CLIENTS:
    TELEGRAM_CLIENTS.update(
        {client['identifier']: TelegramClient(client['identifier'], int(API_ID), API_HASH)})


async def new_message_handler(event, tg_client):
    """ Общий обработчик сообщений, распределяет в соответствующие функции
        в зависимости от типа сообщения: личного/группового
    """

    message = event.message

    if message.is_private:
        return await private_message_handler(tg_client, message)
    return None


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
    try:
        peer = await tg_client.get_entity(identifier)
    except ValueError:
        raise PeerNotFoundError()
    return peer


async def get_peer_info(user_id, tg_client) -> dict:
    """ Получение информации о собеседнике
        @param user_id: id tg-пользователя, можно получить из объекта message (входящего
        из handler-a либо исходящего как результат функции tg_client.send_message).peer_id.user_id
        @param tg_client:
    """

    peer_fields = ['id', 'bot', 'first_name', 'last_name', 'phone', 'username']
    peer_entity = await tg_client.get_entity(user_id)
    peer_info = {field: getattr(peer_entity, field) for field in peer_fields}
    return peer_info


async def serve_client(running_tg_client):
    """ Объявление обработчиков событий из телеграма """

    from server import app
    from telethon import events

    @running_tg_client.on(events.NewMessage())
    async def income_handler(event):
        message_data = await new_message_handler(event, tg_client=running_tg_client)

        if message_data:
            outer_service_url = getattr(running_tg_client, 'outer_service_url')
            phone_number = getattr(running_tg_client, 'phone_number')
            message_data.update({'self_phone_number': phone_number})

            tg_client_identifier = getattr(running_tg_client, 'tg_client_identifier')
            message_data.update({'tg_client_identifier': tg_client_identifier})

            if message_data:
                await app['session'].post(outer_service_url, json=message_data)
