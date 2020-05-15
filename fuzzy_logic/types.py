"""
Luferov Victor <lyferov@yandex.ru>

Types of smths
"""

from enum import Enum


class MfCompositionType(Enum):
    """
    Type composition of mf
    """
    MIN = 1
    MAX = 2
    PROD = 3
    SUM = 4


class AndMethod(Enum):
    """
    Method and
    """
    MIN = 1     # min(a, b)
    PROD = 2    # a * b


class ImplicationMethod(Enum):
    MIN = 1     # Усечение вывода нечетких множеств
    PROD = 2    # Масштабирование вывода нечетких множеств


class OrMethod(Enum):
    MAX = 1     # max(a, b)
    PROB = 2    # a + b - a * b


class AggregationMethod(Enum):
    MAX = 1
    SUM = 2


class DefuzzificationMethod(Enum):
    """
    Methods of defuzzification
    """
    CENTROID = 1
    BISECTOR = 2
    AVERAGE_MAXIMUM = 3


class OperatorType(Enum):
    """
    Type of operator in fuzzy rule base
    """
    AND = 1
    OR = 2


class HedgeType(Enum):
    """
    Hedge modified for terms
    """
    NULL = 0
    SLIGHTLY = 1
    SOMEWHAT = 2
    VERY = 3
    EXTREMELY = 4


class DefazzificationMethod(Enum):
    """
    Метод дефаззификации
    """
    CENTROID = 1
    BISECTOR = 2
    AVERAGE_MAXIMUM = 3
