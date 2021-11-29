""" Обработчики сообщений """

from telegram.message import get_message_content, get_message_author_info


async def income_private_message_handler(tg_client, message):
    """ Обработчик сообщений, полученных в личном чате """
    author = await get_message_author_info(message, tg_client)
    text, media_content, media_content_description, file_name = await get_message_content(message)

    data = {
        'id': message.id,
        'author': author,
        'text': text,
        'media_content': media_content,
        'media_content_description': media_content_description,
        'file_name': file_name
    }
    return data
