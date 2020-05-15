"""
Luferov Victor <lyferov@yandex.ru>

Mamdani Fuzzy System
"""

from typing import List, Dict
from .generic_fs import GenericFuzzySystem
from .rules import FuzzyRule, FuzzyVariable
from .rule_parser import RuleParser
from .mf import MembershipFunction
from .types import AndMethod, OrMethod, OperatorType, ImplicationMethod, AggregationMethod, DefazzificationMethod


class MamdaniFuzzySystem(GenericFuzzySystem):

    def __init__(self,
                 inp: List[FuzzyVariable],
                 out: List[FuzzyVariable],
                 am: AndMethod = AndMethod.PROD,
                 om: OrMethod = OrMethod.MAX,
                 im: ImplicationMethod = ImplicationMethod.MIN,
                 ag: AggregationMethod = AggregationMethod.MAX,
                 dm: DefazzificationMethod = DefazzificationMethod.CENTROID):
        """
        Конструктор создания нечеткой модели мамдани
        :param inp: входящие переменные
        :param out: выходные переменные
        :param am: метод и
        :param om: метод или
        :param im: метод нечеткой импликации
        :param ag: метод неечткого агрегирования
        :param dm: метод дефаззификации
        """
        self.out: List[FuzzyVariable] = out
        self.rules: List[FuzzyRule] = List[FuzzyRule]
        self.implication_method: ImplicationMethod = im
        self.aggregation_method: AggregationMethod = ag
        self.def_method: DefazzificationMethod = dm
        super().__init__(inp, am, om)

    def output_by_name(self, name: str) -> FuzzyVariable:
        """
        Ищем выходную переменную по имени
        :param name: имя переменной
        :return: переменная
        """
        for out in self.out:
            if out.name == name:
                return out
        raise Exception(f'Входной переменной с именем "{name}" не найдено')

    def parse_rule(self, rule: str) -> FuzzyRule:
        """
        Парсим правило из текста
        :param rule: правило в текстовом представлении
        :return: нечеткое правило
        """
        return RuleParser.parse(rule, self.inp, self.out)

    def defuzzify(self, mf: MembershipFunction, min_value: float, max_value: float) -> float:
        if self.def_method == DefazzificationMethod.CENTROID:
            k: int = 1000   # Шаг дефаззицикации
            step = (max_value - min_value) / k
            val_right: float = .0
            val2_right: float = .0
            numerator: float = 0
            denominator: float = 0
            for i in range(k):
                if i == 0:
                    pt_right: float = min_value
                    val_right: float = mf.get_value(pt_right)
                    val2_right: float = pt_right * val_right
                pt_center: float = min_value + step * (i + .5)
                pt_right: float = min_value + step * (i + 1)

                val_left: float = val_right
                val_center: float = mf.get_value(pt_center)
                val_right: float = mf.get_value(pt_right)

                val2_left: float = val2_right
                val2_center: float = pt_center * val_center
                val2_right: float = pt_right * val_right

                numerator += step * (val2_left + 4 * val2_center + val2_right) / 3.0
                denominator += step * (val_left + 4 * val_center + val2_right) / 3.0
            return numerator / denominator
        else:
            raise Exception(f'Метод дефаззификации {self.def_method} не реализован')
