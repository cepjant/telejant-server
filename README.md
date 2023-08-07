
# Веб сервер с клиентом Telegram, предоставляющий возможность получения и отправки сообщений путем отправки и получения запросов на сервер


aiohttp сервер отправляет на указанный вами сервер все входящие личные сообщения (включая медиа, стикеры и голосовые сообщения), а также принимает сообщения для отправки исходящих сообщений. 

# Запуск:
0. Создать виртуальное окружение и установить зависимости из requirements.txt.
1. Запустить: 
`python manage.py server.py`
2. Для подключения телеграм-аккаунта необходимо отправить на сервер POST запрос со следующими данными:

`phone_number` - номер телефона аккаунта;
`endpoint_url` - урл, на который нужно отправлять входящие сообщения;
`passcode_access_key` - сгенерированный на вашей стороне ключ для доступа к коду подтверждения
`tg_client_identifier` - идентификатор создаваемого клиента (UUID) 

3. Сервис отправит POST запрос на endpoint_url для получения кода подтверждения со следующими данными:
`{"required": "passcode", "access_key": passcode_access_key}`
В ответ необходимо отправить строку с полученным в телеграме кодом. 

# Взаимодействие: 

1. Все входящие сообщения сервис будет отправлять POST запросом на endpoint_url:

`{'id': 115, 'peer': {'id': telegram_user_id, 'bot': True/False, 'first_name': telegram_first_name, 'last_name': telegram_last_name, 'phone': telegram_phone_number, 'username': username}, 'text': 'Test', 'media_content': base64, 'media_content_description': picture/sticker..., 'file_name': None, 'direction': 'income', 'tg_client_identifier': UUID}`

2. Для отправки исходящего сообщения необходимо отправить POST-запрос с следующими данными:

`{'user': {'user_id': user_id}, 'tg_client_identifier': UUID, 'text': 'test'}`
Вместо {'user_id': user_id} допускается {'username': username} либо {'phone_number': phone_number}.

3. Для получения статуса телеграм клиента (Connected, Disconnected, NotFound) необходимо отправить GET запрос по адресу

`http://0.0.0.0:8080/status/?telegram_guid=UUID`
