import asyncio
import concurrent.futures
import os 


def _get_session_files():
    """ Возвращает файлы сессий телеграма """ 

    session_dir_files = [f for f in os.listdir("telegram/sessions") if f.endswith('.session')]
    return session_dir_files

def _start_session_files(fut):
    """ Запускает сессии, названия файлов которых получены в fut.result() """ 
    print(fut.result())

async def start_sessions_from_files():
    """ Ищет запущенные раннее сессии и пытается их запустить """ 

    loop = asyncio.get_event_loop()

    with concurrent.futures.ProcessPoolExecutor() as executor:
       fut = loop.run_in_executor(executor, _get_session_files)
       fut.add_done_callback(_start_session_files)
