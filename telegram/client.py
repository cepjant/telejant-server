""" Клиент телеграм - получение и отправка сообщений """

from telegram.handlers import income_private_message_handler
from settings import API_ID, API_HASH
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChannel

telegram_client = TelegramClient('session_name_1', int(API_ID), API_HASH)


@telegram_client.on(events.NewMessage(incoming=True))
async def income_handler(event):
    """ Общий обработчик входящих сообщений, распределяет в соответствующие функции
        в зависимости от типа сообщения: личного/группового
    """

    message = event.message

    # источник получения сообщения (либо канал, либо личный чат)
    peer = message.peer_id

    if isinstance(peer, PeerUser):
        # личный диалог
        await income_private_message_handler(telegram_client, message)

    elif isinstance(peer, PeerChannel):
        # групповой диалог / канал
        pass


async def send_telegram_message(username, text):
    """ Отправка сообщений """
    await telegram_client.send_message(username, text)
