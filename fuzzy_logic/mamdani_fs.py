"""
Luferov Victor <lyferov@yandex.ru>

Mamdani Fuzzy System
"""

from typing import List, Dict
from .generic_fs import GenericFuzzySystem
from .rules import FuzzyRule, FuzzyVariable
from .rule_parser import RuleParser
from .mf import MembershipFunction, CompositeMF, ConstantMF
from .types import AndMethod, \
    OrMethod, \
    OperatorType, \
    ImplicationMethod, \
    AggregationMethod, \
    DefazzificationMethod, \
    MfCompositionType


class MamdaniFuzzySystem(GenericFuzzySystem):
    """

    """

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

    def implicate(self, conditions: Dict[FuzzyRule, float]) -> Dict[FuzzyRule, MembershipFunction]:
        def implicate_type(it: ImplicationMethod) -> MfCompositionType:
            if it == ImplicationMethod.MIN:
                return MfCompositionType.MIN
            elif it == ImplicationMethod.PROD:
                return MfCompositionType.PROD
            raise Exception(f'Тип композиции {it} не найден')
        return {
            rule: CompositeMF(
                implicate_type(self.implication_method),
                ConstantMF(value),
                rule.conclusion.term.mf) for rule, value in conditions.items()
        }

    def aggregate(self, conclusions: Dict[FuzzyRule, MembershipFunction]) -> Dict[FuzzyVariable, MembershipFunction]:
        """
        Процедура агрегации
        :param conclusions: заключения
        :return:
        """
        def composite_type(am: AggregationMethod) -> MfCompositionType:
            if am == AggregationMethod.MAX:
                return MfCompositionType.MAX
            elif am == AggregationMethod.SUM:
                return MfCompositionType.SUM
            raise Exception(f'Тип композиции {am} не найден')
        return {
            variable: CompositeMF(
                composite_type(self.aggregation_method),
                *[mf for rule, mf in conclusions.items() if rule.conclusion.variable == variable]
            ) for variable in self.out
        }

    def defuzzify(self, fr: Dict[FuzzyVariable, MembershipFunction]) -> Dict[FuzzyVariable, float]:
        """
        Дефаззификация нечеткой переменной
        :param fr: fuzzyResult - результат нечеткой входной переменной
        :return: результат дефаззификации
        """
        return {variable: self.__defuzzify(mf, variable.min_value, variable.max_value) for variable, mf in fr.items()}

    def __defuzzify(self, mf: MembershipFunction, min_value: float, max_value: float) -> float:
        """
        Дефаззификация значения
        :param mf: лингвистический терм
        :param min_value: минимальное значение
        :param max_value: максимальное значение
        :return:
        """
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
