"""
Luferov Victor <lyferov@yandex.ru>

Fuzzy Rules
"""
from typing import List
from abc import ABC, abstractmethod
from .terms import Term
from .types import OperatorType, HedgeType
from .variables import FuzzyVariable, SugenoVariable


class SingleCondition:

    def __init__(self, variable: [FuzzyVariable, SugenoVariable], term: Term, _not: bool = False):
        self.variable: [FuzzyVariable, SugenoVariable] = variable
        self.term: Term = term
        self._not: bool = _not


class Conditions:

    def __init__(self, conditions: List, op: OperatorType = OperatorType.AND, _not: bool = False):
        self.conditions: List = conditions
        self.op: OperatorType = op
        self._not: bool = _not


class FuzzyCondition(SingleCondition):
    """
    Fuzzy rule
    """

    def __init__(self,
                 variable: [FuzzyVariable, SugenoVariable],
                 term: Term,
                 _not: bool = False,
                 hedge: HedgeType = HedgeType.NULL):

        super().__init__(variable, term, _not)
        self.hedge: HedgeType = hedge


class ParsableRule(ABC):

    @property
    @abstractmethod
    def condition(self) -> Conditions:
        """
        getter path of "if" in condition
        :return:
        """
        ...

    @condition.setter
    @abstractmethod
    def condition(self, value: Conditions):
        """
        setter path of "if" in condition
        :param value:
        :return:
        """
        ...

    @property
    @abstractmethod
    def single_condition(self) -> SingleCondition:
        """
        getter path of "then" in condition
        :return:
        """
        ...

    @single_condition.setter
    @abstractmethod
    def single_condition(self, value: SingleCondition):
        """
        setter path of "then" in condition
        :param value:
        :return:
        """
        ...
