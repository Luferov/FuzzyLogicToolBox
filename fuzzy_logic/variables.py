"""
Luferov Victor <lyferov@yandex.ru>

Fuzzy Variable
    - Mamdani
    - Sugeno
"""

from typing import List
from .terms import Term


class FuzzyVariable:

    def __init__(self, name: str, min_value: float = 0.0, max_value: float = 1.0, *terms: Term):
        if min >= max:
            raise ValueError(f'{min} <= {max} is not True')
        self.name: str = name
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.terms: List[Term] = list(terms)

