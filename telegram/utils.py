""" Вспомогательные функции """
import os

from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeSticker


def get_message_media_document(message):
    """ Получение медиа объектов, сгруппированных Telethon'ом в категорию Document,
    например стикеры
    """
    content = ""
    for attr in message.document.attributes:
        if isinstance(attr, DocumentAttributeSticker):
            content = 'Стикер (эмодзи-альтрентива:' + attr.alt + ')'
    return content


async def get_message_media_photo(message):
    """ Получение фотографии из сообщения (фотография скачивается методами Telethon),
     переводится в base64, резльутат возвращается, а фотография удаляется. """
    path = await message.download_media()
    with open(path, 'rb') as image_file:
        file = image_file.read()
    os.remove(path)
    return file


async def get_message_content(message):
    """ Получение содержимого сообщения """
    media_content = b""
    content = ""
    if message.message:
        content = message.message
    else:
        if message.media:
            media = message.media
            if isinstance(media, MessageMediaDocument):
                content = get_message_media_document(message)
            elif isinstance(media, MessageMediaPhoto):
                media_content = await get_message_media_photo(message)
                content = 'фотография'

    return content, media_content
