""" Клиент телеграм - получение и отправка сообщений """

import phonenumbers
from telethon import TelegramClient

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
    else:
        return None

    try:
        user = await telegram_client.get_entity(identifier)
    except ValueError:
        raise PeerNotFoundError()

    return await telegram_client.send_message(user, text, file=file, attributes=attributes)
