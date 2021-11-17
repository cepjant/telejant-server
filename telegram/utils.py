""" Вспомогательные функции, испольщующиеся в нескольких местах """


def get_message_media_document(media):
    content = ""
    for attr in media['document'].get('attributes', []):
        if attr['_'] == 'DocumentAttributeSticker':
            content = 'Стикер (эмодзи-альтрентива:' + attr['alt'] + ')'
    return content


def get_message_content(message):
    content = ""
    if message.get('message'):
        content = message.get('message')
    else:
        if message.get('media'):
            media = message.get('media')
            if media['_'] == 'MessageMediaDocument':
                content = get_message_media_document(media)
            elif media['_'] == 'MessageMediaPhoto':
                pass

    return content
