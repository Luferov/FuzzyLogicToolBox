"""
Luferov Victor <lyferov@yandex.ru>

Rule Parser
"""
from typing import List
from abc import ABC, abstractmethod


class NameHelper:

    @staticmethod
    @property
    def keywords() -> List[str]:
        """
        Ключевые слова нечеткой продукционной базы правил
        :return: список ключевых слов
        """
        return [
            'if',
            'then',
            'is',
            'and',
            'or',
            'not',
            '(',
            ')',
            'slightly',
            'somewhat',
            'very',
            'extremely'
        ]

    @staticmethod
    def valid_name(name: str) -> bool:
        """
        Проверяем чтобы имя ключевого слоя не было равно нулю и не было в ключевых переменных
        :param name: имя токена
        :return: валидное имя или нет
        """
        if len(name) == 0:
            return False
        if name in NameHelper.keywords:
            return False
        return True


class Expression(ABC):
    """
    Abstract class of expressions
    """
    @property
    @abstractmethod
    def text(self) -> str:
        ...


class AlternativeLexem(ABC):
    """
    Alternative lexem
    """

    @property
    @abstractmethod
    def alternative(self) -> 'AlternativeLexem':
        ...

    @alternative.setter
    @abstractmethod
    def alternative(self, value: 'AlternativeLexem') -> 'AlternativeLexem':
        ...


class Lexem(Expression):
    """
    Abstract class of Lexems
    """

    @property
    @abstractmethod
    def text(self) -> str:
        ...

    @abstractmethod
    def __str__(self):
        return self.text




