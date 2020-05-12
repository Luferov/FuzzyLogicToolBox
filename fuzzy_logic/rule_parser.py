"""
Luferov Victor <lyferov@yandex.ru>

Rule Parser
"""
from typing import List, Dict
from abc import ABC, abstractmethod
from .rules import FuzzyCondition
from .terms import Term
from .variables import FuzzyVariable, SugenoVariable, SugenoFunction


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


class RuleParser:
    """
    Парсим нечеткое правило на лексемы
    """

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
        def alternative(self) -> 'RuleParser.AlternativeLexem':
            ...

        @alternative.setter
        @abstractmethod
        def alternative(self, value: 'RuleParser.AlternativeLexem') -> 'RuleParser.AlternativeLexem':
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

    class KeywordLexem(Lexem):

        def __init__(self, name: str):
            self.name: str = name

        @property
        def text(self) -> str:
            return self.name

        def __str__(self):
            return self.text

    class VarLexem(Lexem):
        """
        Лексема нечеткой переменной
        """

        def __init__(self, variable: [FuzzyVariable, SugenoVariable], inp: bool):
            """
            Лексема нечеткой переменной
            :param variable: Нечеткая переменная
            :param inp: флаг входной переменной нечеткой базы правил
            """
            self.variable: [FuzzyVariable, SugenoVariable] = variable
            self.input: bool = inp

        @property
        def text(self) -> str:
            return self.variable.name

        def __str__(self):
            return self.text

    class TermLexem(Lexem, AlternativeLexem):
        """
        Лексема нечеткого терма
        """

        def __init__(self, term: [Term, SugenoFunction], inp: bool = True):
            self.term: [Term, SugenoFunction] = term
            self.input: bool = inp
            self.alternative_term: [RuleParser.AlternativeLexem, None] = None

        @property
        def alternative(self) -> 'RuleParser.AlternativeLexem':
            return self.alternative_term

        @alternative.setter
        def alternative(self, value: 'RuleParser.AlternativeLexem'):
            self.alternative_term = value

        @property
        def text(self) -> str:
            return self.term.name

        def __str__(self):
            return self.text

    class ConditionExpression(Lexem):
        def __init__(self, expressions: List['RuleParser.Expression'], condition: FuzzyCondition):
            self.expressions: List['RuleParser.Expression'] = expressions
            self.condition: FuzzyCondition = condition

        @property
        def text(self) -> str:
            """
            Возвращаем текст состояния правила
            :return:
            """
            return ''.join([expression.text for expression in self.expressions])

        def __str__(self):
            return self.text

    def __init__(self):

        pass




