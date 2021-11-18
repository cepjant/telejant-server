""" Обработчики сообщений """

from telegram.utils import get_message_content


async def income_private_message_handler(tg_client, message):
    """ Обработчик сообщений, полученных в личном чате """
    user_id = message.peer_id.user_id
    user_entity = await tg_client.get_entity(user_id)
    text, media_content, media_content_description = await get_message_content(message)
    message = ''
    message += (text or "") + " "
    message += (str(media_content)[:10] if media_content else "") + " "
    message += media_content_description or " "
    print('Сообщение от', user_entity.username, '--', message)
