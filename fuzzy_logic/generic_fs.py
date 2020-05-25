"""
Luferov Victor <lyferov@yandex.ru>

Generic fuzzy system
"""

from typing import List, Dict
from collections import defaultdict
from .variables import FuzzyVariable
from .rules import FuzzyRule
from .terms import Term
from .rules import Conditions, FuzzyCondition
from .types import AndMethod, OrMethod, OperatorType, HedgeType


class GenericFuzzySystem:
    """
    Обобщенная модель нечеткой логики
    """

    def __init__(self,
                 inp: List[FuzzyVariable],
                 am: AndMethod = AndMethod.PROD,
                 om: OrMethod = OrMethod.MAX):
        self.inp: List[FuzzyVariable] = inp
        self.rules: List[FuzzyRule] = []
        self.and_method: AndMethod = am
        self.or_method: OrMethod = om

    def input_by_name(self, name: str) -> FuzzyVariable:
        """
        Ищем переменную по имени
        :param name: имя переменной
        :return: возвращаемая переменная
        """
        for inp in self.inp:
            if inp.name == name:
                return inp
        raise Exception(f'Выходной переменной с именем "{name}" не найдено')

    def evaluate_conditions(self, fi: Dict[FuzzyVariable, Dict[Term, float]]) -> Dict[FuzzyRule, float]:
        """
        Расчитываем заключения по нечетким правилам
        :param fi: фаззицицированные входные переменные
        :return:
        """
        return {rule: self.evaluate_condition(rule.condition, fi) for rule in self.rules}

    def fuzzify(self, inp: Dict[FuzzyVariable, float]) -> Dict[FuzzyVariable, Dict[Term, float]]:
        """
        Фаззификация значений
        :param inp:
        :return:
        """
        self.validate_input_values(inp)
        result: Dict[FuzzyVariable, Dict[Term, float]] = defaultdict(Dict[Term, float])
        for variable in self.inp:
            result[variable] = defaultdict(float)
            for term in variable.terms:
                result[variable][term] = term.mf.get_value(inp[variable])
        return result

    def evaluate_condition(self,
                           condition: [Conditions, FuzzyCondition],
                           fi: Dict[FuzzyVariable, Dict[Term, float]]) -> float:
        """
        Вычисляем условие
        :param condition: условиие
        :param fi: fuzzyInput входные данные
        :return:
        """
        if isinstance(condition, Conditions):
            if len(condition.conditions) == 0:
                raise Exception('Сотояний нет')
            elif len(condition.conditions) == 1:
                result: float = self.evaluate_condition(condition.conditions[0], fi)
            else:
                result: float = self.evaluate_condition(condition.conditions[0], fi)
                for i in range(1, len(condition.conditions)):
                    result = self.evaluate_condition_pair(
                        result,
                        self.evaluate_condition(condition.conditions[i], fi),
                        condition.op)
            return 1.0 - result if condition.not_ else result
        elif isinstance(condition, FuzzyCondition):
            result: float = fi[condition.variable][condition.term.term]
            # Навешиваем модификатор
            if condition.hedge == HedgeType.SLIGHTLY:
                result = result ** (1. / 3.)
            elif condition.hedge == HedgeType.SOMEWHAT:
                result = result ** .5
            elif condition.hedge == HedgeType.VERY:
                result *= result
            elif condition.hedge == HedgeType.EXTREMELY:
                result = result ** 3
            return 1.0 - result if condition.not_ else result
        else:
            raise Exception('Не найдено условие в нечетком правиле')

    def evaluate_condition_pair(self, condition1: float, condition2: float, op: OperatorType) -> float:
        if op == OperatorType.AND:
            if self.and_method == AndMethod.MIN:
                return min(condition1, condition2)
            elif self.and_method == AndMethod.PROD:
                return condition1 * condition2
            else:
                raise Exception('Оператор метода "И" не найден')
        elif op == OperatorType.OR:
            if self.or_method == OrMethod.MAX:
                return max(condition1, condition2)
            elif self.or_method == OrMethod.PROB:
                return condition1 + condition2 - condition1 * condition2
            else:
                raise Exception('Оператор метода "ИЛИ" не найден')
        else:
            raise Exception('Оператор композиции не найден')

    def validate_input_values(self, inp: Dict[FuzzyVariable, float]):
        """
        Проверка валидности входных переменных
        :param inp: проверяем входящие значения
        :return:
        """
        if len(inp) != len(self.inp):
            raise Exception('Количество входных значений не верно')
        for variable in self.inp:
            if variable in inp:
                value: float = inp[variable]
                if not variable.min_value <= value <= variable.max_value:
                    raise Exception('Значние переменной выходит за диапазон')
            else:
                raise Exception(f'Значение переменной {variable.name} не найдено')
