import asyncio

from aiohttp import web

from telegram.handlers import income_private_message_handler
from settings import API_ID, API_HASH
from telethon import TelegramClient, events

telegram_client = TelegramClient('session_name_1', int(API_ID), API_HASH)


@telegram_client.on(events.NewMessage(incoming=True))
async def income_handler(event):
    """ Общий обработчик входящих сообщений, распределяет в соответствующие функции
        в зависимости от типа сообщения: личного/группового
    """

    message_dict = event.message.to_dict()

    # источник получения сообщения (либо канал, либо личный чат)
    peer = message_dict['peer_id']['_']

    if peer == 'PeerUser':
        # личный диалогSS
        await income_private_message_handler(telegram_client, message_dict)

    elif peer == 'PeerChannel':
        # групповой диалог / канал
        pass


async def send_telegram_message(username, text):
    await telegram_client.send_message(username, text)
