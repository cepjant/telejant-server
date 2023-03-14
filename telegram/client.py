""" Клиент телеграм - получение и отправка сообщений """

import phonenumbers
import random
from telethon import functions, types

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
