""" Клиент телеграм - получение и отправка сообщений """
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChannel

from settings import API_ID, API_HASH
from telegram.handlers import income_private_message_handler

telegram_client = TelegramClient('session_name_1', int(API_ID), API_HASH)


async def client_income_handler(event):
    """ Общий обработчик входящих сообщений, распределяет в соответствующие функции
        в зависимости от типа сообщения: личного/группового
    """

    message = event.message

    # источник получения сообщения (либо канал, либо личный чат)
    peer = message.peer_id

    if isinstance(peer, PeerUser):
        # личный диалог
        return await income_private_message_handler(telegram_client, message)

    elif isinstance(peer, PeerChannel):
        # групповой диалог / канал
        return None


async def send_telegram_message(user, text):
    """ Отправка сообщений """
    if user.get('user_id'):
        identifier = int(user.get('user_id'))
    elif user.get('username'):
        identifier = user.get('username')
    else:
        return None
    user = await telegram_client.get_entity(identifier)
    return await telegram_client.send_message(user, text)
