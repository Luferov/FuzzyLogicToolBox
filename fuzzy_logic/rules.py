"""
Luferov Victor <lyferov@yandex.ru>

Fuzzy Rules
"""
from typing import List
from .terms import Term
from .types import OperatorType, HedgeType
from .variables import FuzzyVariable, SugenoVariable, SugenoFunction


class SingleCondition:
    """
    Единичное заключение
    FuzzyVariable - Term
    SugenoVariable - SugenoFunction
    """

    def __init__(self, variable: [FuzzyVariable, SugenoVariable], term: [Term, SugenoFunction], not_: bool = False):
        self.variable: [FuzzyVariable, SugenoVariable] = variable
        self.term: [Term, SugenoFunction] = term
        self.not_: bool = not_


class Conditions:

    def __init__(self, conditions: [List, None] = None, op: OperatorType = OperatorType.AND, not_: bool = False):
        self.conditions: List = conditions if conditions is not None else []
        self.op: OperatorType = op
        self.__not: bool = not_

    @property
    def not_(self):
        return self.__not


class FuzzyCondition(SingleCondition):
    """
    Fuzzy rule
    """

    def __init__(self,
                 variable: [FuzzyVariable, SugenoVariable],
                 term: [Term, SugenoFunction],
                 not_: bool = False,
                 hedge: HedgeType = HedgeType.NULL):

        super().__init__(variable, term, not_)
        self.hedge: HedgeType = hedge


class FuzzyRule:
    """
    Обобщенная модель нечеткого правила
        - Нечеткое условие "condition" для Sugeno и Mamdani одинаковые

        - Нечеткое заключение conclusion для Sugeno
            conclusion: SingleConclusion = SingleConclusion(SugenoVariable, SugenoFunction, not?)
         - Нечеткое заключение conclusion для Mamdani
            conclusion: SingleConclusion = SingleConclusion(FuzzyVariable, Term, not?)
    """

    def __init__(self, condition: Conditions, conclusion: SingleCondition, weight: float = 1.):
        """
        Конструктоур нечеткого правила мамдани
        :param condition: условие в блоке IF
        :param conclusion: условие в блоке THEN
        :param weight: дополнительный вес правила
        """
        self.condition: Conditions = condition
        self.conclusion: SingleCondition = conclusion
        self.weight: float = weight
