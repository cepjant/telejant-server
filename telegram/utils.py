""" Вспомогательные функции, испольщующиеся в нескольких местах """
import os

from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeSticker


def get_message_media_document(message):
    content = ""
    for attr in message.document.attributes:
        if isinstance(attr, DocumentAttributeSticker):
            content = 'Стикер (эмодзи-альтрентива:' + attr.alt + ')'
    return content


async def get_message_media_photo(message):
    path = await message.download_media()
    with open(path, 'rb') as f:
        file = f.read()
    os.remove(path)
    return file


async def get_message_content(message):
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
