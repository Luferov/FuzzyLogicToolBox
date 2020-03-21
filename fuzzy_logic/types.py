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
