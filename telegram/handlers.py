""" Обработчики сообщений """

from telegram.message import get_message_content


async def private_message_handler(tg_client, message):
    """ Обработчик сообщений, полученных или отправленных в личном чате """
    from telegram.client import get_peer_info

    peer = await get_peer_info(message.peer_id.user_id, tg_client)
    text, media_content, media_content_description, file_name = await get_message_content(message)

    data = {
        'id': message.id,
        'peer': peer,
        'text': text,
        'media_content': media_content,
        'media_content_description': media_content_description,
        'file_name': file_name,
        'direction': 'outcome' if message.out else 'income'
    }
    return data
