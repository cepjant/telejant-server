""" Клиент телеграм - получение и отправка сообщений """

import phonenumbers
import random
from telethon import TelegramClient
from telethon import functions, types

from settings import API_ID, API_HASH
from telegram.exceptions import PeerNotFoundError
from telegram.handlers import private_message_handler

telegram_client = TelegramClient('session_name_1', int(API_ID), API_HASH)


async def client_handler(event):
    """ Общий обработчик сообщений, распределяет в соответствующие функции
        в зависимости от типа сообщения: личного/группового
    """

    message = event.message

    if message.is_private:
        return await private_message_handler(telegram_client, message)
    return None


async def send_telegram_message(user, text, file=None, attributes=None):
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
        await add_contact(identifier)
    else:
        return None

    peer = await get_peer(identifier)
    return await telegram_client.send_message(peer, text, file=file, attributes=attributes)


async def add_contact(phone_number: str):
    """ При отправке пользователю по номеру телефона предварительно нужно добавить его в
        контакты """
    await telegram_client(functions.contacts.ImportContactsRequest(
        contacts=[types.InputPhoneContact(
            client_id=random.randrange(-2 ** 63, 2 ** 63),
            phone=phone_number,
            first_name='',
            last_name=''
        )]
    ))


async def get_peer(identifier):
    """ Получение пользователя для отправки сообщения. """
    try:
        peer = await telegram_client.get_entity(identifier)
    except ValueError:
        raise PeerNotFoundError()
    return peer
