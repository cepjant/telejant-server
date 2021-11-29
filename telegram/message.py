""" Функции для обработки сообщений и получения из них информации """

import base64
import os

from telethon.tl.types import (
    MessageMediaDocument, MessageMediaPhoto, DocumentAttributeSticker, DocumentAttributeAudio,
    DocumentAttributeFilename
)


async def get_message_content(message):
    """ Получение содержимого сообщения """
    text = None  # текст сообщения (сообщение может содержать текст + изображение)
    base64_content = None  # base64 изображения/стикера
    media_content_description = None  # описание файла
    file_name = None  # название файла
    if message.message:
        text = message.message
    if message.media:
        base64_content, media_content_description, file_name = await get_message_media(message)

    return text, base64_content, media_content_description, file_name


async def get_peer_info(message, tg_client):
    """ Получение информации о собеседнике """

    peer_fields = ['id', 'bot', 'first_name', 'last_name', 'phone', 'username']

    peer_id = message.peer_id.user_id
    peer_entity = await tg_client.get_entity(peer_id)
    peer_info = {field: getattr(peer_entity, field) for field in peer_fields}
    return peer_info


async def get_message_media(message):
    """ Получение содержимого медиа файлов (стикеров, изображений) из сообщения """
    base64_content = None
    media_content_description = None
    file_name = None
    if isinstance(message.media, MessageMediaDocument):
        base64_content, media_content_description, file_name = await _get_document_content(message)
    elif isinstance(message.media, MessageMediaPhoto):
        base64_content, file_name = await _get_media_content(message)
        media_content_description = 'picture'
    return base64_content, media_content_description, file_name


async def _get_document_content(message):
    """ Получение медиа объектов, сгруппированных Telethon'ом в категорию Document,
    например стикеры
    """
    base64_content = None
    content_description = None
    file_name = None
    for attr in message.document.attributes:
        if isinstance(attr, DocumentAttributeSticker):
            base64_content, file_name = await _get_media_content(message)
        elif isinstance(attr, DocumentAttributeAudio) and attr.voice:
            base64_content, file_name = await _get_media_content(message)
            content_description = 'audio_message'
        elif isinstance(attr, DocumentAttributeFilename):
            if attr.file_name == 'sticker.webp':
                content_description = 'sticker'
            elif attr.file_name == 'AnimatedSticker.tgs':
                content_description = 'animated_sticker'

    return base64_content, content_description, file_name


async def _get_media_content(message):
    """ Загружает медиа (стикер, изображение), возвращает данные, а медиа удаляет с диска """
    path = await message.download_media()
    with open(path, 'rb') as sticker_file:
        content = sticker_file.read()
    os.remove(path)
    encoded = base64.b64encode(content).decode('ascii')
    return encoded, path
