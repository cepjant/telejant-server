""" Исключения модуля telegram """


class PeerNotFoundError(Exception):
    """ Пользователь с переданными параметрами не найден """
    pass
