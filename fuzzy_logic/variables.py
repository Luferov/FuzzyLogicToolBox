"""
Luferov Victor <lyferov@yandex.ru>

Fuzzy Variable
    - Mamdani
    - Sugeno
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from .terms import Term


class FuzzyVariable:

    def __init__(self, name: str, min_value: float = 0.0, max_value: float = 1.0, *terms: Term):
        if min_value >= max_value:
            raise ValueError(f'{min_value} <= {max_value} is not True')
        self.name: str = name
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.terms: List[Term] = list(terms)

    def term_by_name(self, name: str) -> Term or None:
        """
        Find term by name
        :param name: name of term
        :return: term
        """
        for term in self.terms:
            if term.name == name:
                return term

    @property
    def values(self):
        return self.terms


class SugenoFunction(ABC):
    """
    Sugeno function interfaces
    """
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def evaluate(self, inputs: Dict[FuzzyVariable, float]) -> float:
        ...


class LinearSugenoFunction(SugenoFunction):

    def __init__(self, name: str, coefficients: Dict[FuzzyVariable, float], const: float = .0):
        self.__name: str = name
        self.coefficients: Dict[FuzzyVariable, float] = coefficients
        self.const: float = const

    @property
    def name(self) -> str:
        return self.__name

    def evaluate(self, inputs: Dict[FuzzyVariable, float]) -> float:
        """
        Calculate linear function
        :param inputs: Values
        :return: result of calculation
        """
        return self.const + sum([self.coefficients[variable] * value for variable, value in inputs.items()])


class SugenoVariable:
    """
    Sugeno variable
    """

    def __init__(self, name: str, *functions: SugenoFunction):
        self.name: str = name
        self.functions: List[SugenoFunction] = list(functions)

    def function_by_name(self, name: str) -> SugenoFunction:
        for function in self.functions:
            if function.name == name:
                return function

    @property
    def values(self):
        return self.functions
