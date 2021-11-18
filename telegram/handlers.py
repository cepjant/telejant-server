""" Обработчики сообщений """

from telegram.message import get_message_content, get_message_author_info


async def income_private_message_handler(tg_client, message):
    """ Обработчик сообщений, полученных в личном чате """
    author = await get_message_author_info(message, tg_client)
    text, media_content, media_content_description = await get_message_content(message)

    message = ''
    message += (text or "") + " "
    message += (str(media_content)[:10] if media_content else "") + " "
    message += media_content_description or " "
    print('Сообщение от', author, '--', message)
