""" Обработчики сообщений """

from telegram.utils import get_message_content


async def income_private_message_handler(tg_client, message):
    """ Обработчик сообщений, полученных в личном чате """
    user_id = message.peer_id.user_id
    user_entity = await tg_client.get_entity(user_id)
    content, media_content = await get_message_content(message)
    print('Сообщение от', user_entity.username, '--', content)


#
# async def handler(event):
#
#     if from_id:
#         message = ''
#         if message_dict.get('message'):
#             message = message_dict.get('message')
#         else:
#             if message_dict.get('media'):
#                 if message_dict.get('media')['_'] == 'MessageMediaDocument':
#
#                     for att in message_dict['media']['document'].get('attributes', []):
#                         if att['_'] == 'DocumentAttributeSticker':
#                             message = 'Стикер (эмодзи-альтрентива:' + att['alt'] + ')'
#
#         entity = await telegram_client.get_entity(from_id)
#         print('Сообщение от', entity.username, ':', message)
