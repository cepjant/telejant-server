""" Вспомогательные функции, испольщующиеся в нескольких местах """
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeSticker


def get_message_media_document(message):
    content = ""
    for attr in message.document.attributes:
        if isinstance(attr, DocumentAttributeSticker):
            content = 'Стикер (эмодзи-альтрентива:' + attr.alt + ')'
    return content


def get_message_content(message):
    content = ""
    if message.message:
        content = message.message
    else:
        if message.media:
            media = message.media
            if isinstance(media, MessageMediaDocument):
                content = get_message_media_document(message)
            elif isinstance(media, MessageMediaPhoto):
                pass

    return content
