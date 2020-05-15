"""
Luferov Victor <lyferov@yandex.ru>

Generic fuzzy system
"""

from typing import List, Dict, Tuple
from collections import defaultdict
from .variables import FuzzyVariable
from .terms import Term
from .types import AndMethod, OrMethod


class GenericFuzzySystem:
    """
    Обобщенная модель нечеткой логики
    """

    def __init__(self, inp: List[FuzzyVariable], am: AndMethod = AndMethod.PROD, om: OrMethod = OrMethod.MAX):
        self.inp: List[FuzzyVariable] = inp
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

    def fuzzify(self, inp: Dict[FuzzyVariable, float]) -> Dict[FuzzyVariable, Dict[Term, float]]:
        """
        Фаззификация значений
        :param inp:
        :return:
        """
        self.validate_input_values(inp)
        result: Dict[FuzzyVariable, Dict[Term, float]] = defaultdict(Dict[Term, float])
        for variable in self.inp:
            for term in variable.terms:
                result[variable][term] = term.mf.get_value(inp[variable])
        return result

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
