""" Вспомогательные функции """
import os

from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeSticker


async def get_message_content(message):
    """ Получение содержимого сообщения """
    text = None  # текст сообщения (сообщение может содержать текст + изображение)
    media_content = None  # base64 изображения/стикера
    media_content_description = None  # описание файла
    if message.message:
        text = message.message
    if message.media:
        media_content, media_content_description = await get_message_media(message)

    return text, media_content, media_content_description


async def get_message_media(message):
    """ Получение содержимого медиа файлов (стикеров, изображений) из сообщения """
    media_content = None
    media_content_description = None
    if isinstance(message.media, MessageMediaDocument):
        media_content, media_content_description = await _get_document_content(message)
    elif isinstance(message.media, MessageMediaPhoto):
        media_content = await _get_media_content(message)
        media_content_description = 'фотография'
    return media_content, media_content_description


async def _get_document_content(message):
    """ Получение медиа объектов, сгруппированных Telethon'ом в категорию Document,
    например стикеры
    """
    content = None
    content_description = None
    for attr in message.document.attributes:
        if isinstance(attr, DocumentAttributeSticker):
            content = await _get_media_content(message)
            content_description = 'Стикер (эмодзи-альтернатива:' + attr.alt + ')'
    return content, content_description


async def _get_media_content(message):
    """ Загружает медиа (стикер, изображение), возвращает данные, а медиа удаляет с диска """
    path = await message.download_media()
    with open(path, 'rb') as sticker_file:
        content = sticker_file.read()
    os.remove(path)
    return content
