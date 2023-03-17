import asyncio
import concurrent.futures
import os

from telegram.client import start_new_session


def _get_session_files():
    """ Возвращает файлы сессий телеграма """

    session_dir_files = [f for f in os.listdir("telegram/sessions") if f.endswith('.session')]
    return session_dir_files


async def start_sessions_from_files(application):
    """ Ищет запущенные раннее сессии и пытается их запустить """

    loop = asyncio.get_event_loop()

    def _start_session_files(future):
        """ Запускает сессии, названия файлов которых получены в fut.result() """
        filenames = future.result()
        for filename in filenames:
            session_name = filename.replace('.session', '')
            print(session_name)
            tg_client_identifier, phone_number = session_name.split('_')
            task = start_new_session(app=application, tg_client_identifier=tg_client_identifier,
                                     phone_number=phone_number)
            loop.create_task(task)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        fut = loop.run_in_executor(executor, _get_session_files)
        fut.add_done_callback(_start_session_files)
