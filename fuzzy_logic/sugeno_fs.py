"""
Luferov Victor <lyferov@yandex.ru>

Sugeno Fuzzy System
"""
from typing import Dict, List
from collections import defaultdict
from .generic_fs import GenericFuzzySystem
from .rules import FuzzyRule
from .rule_parser import RuleParser
from .variables import FuzzyVariable, SugenoVariable, SugenoFunction
from .terms import Term
from .types import AndMethod, OrMethod


class SugenoFuzzySystem(GenericFuzzySystem):

    def __init__(self,
                 inp: List[FuzzyVariable] = List[FuzzyVariable],
                 out: List[SugenoVariable] = List[SugenoVariable],
                 am: AndMethod = AndMethod.PROD,
                 om: OrMethod = OrMethod.MAX):
        """
        Конструктор создания нечеткой переменной сугено
        :param inp: входящие переменные
        :param out: выходные переменные
        :param am: метод И
        :param om: метод ИЛИ
        """
        self.out: List[SugenoVariable] = out
        super().__init__(inp, am, om)

    def output_by_name(self, name: str) -> SugenoVariable:
        """
        Ищем выходную переменную по имени
        :param name: имя переменной
        :return: переменная "variable.SugenoVariable"
        """
        for out in self.out:
            if out.name == name:
                return out
        raise Exception(f'Выходной переменной с именем "{name}" не найдено')

    def parse_rule(self, rule: str) -> FuzzyRule:
        """
        Парсим правило из текста
        :param rule: правило в текстовом представлении
        :return: нечеткое правило
        """
        return RuleParser.parse(rule, self.inp, self.out)

    def evaluate_functions(self, iv: Dict[FuzzyVariable, float]) -> Dict[SugenoVariable, Dict[SugenoFunction, float]]:
        return {variable: {sf: sf.evaluate(iv) for sf in variable.functions} for variable in self.out}

    def combine_result(self,
                       rw: Dict[FuzzyRule, float],
                       fr: Dict[SugenoVariable, Dict[SugenoFunction, float]]) -> Dict[SugenoVariable, float]:
        """
        Объединяем результаты функцию и правил
        :param rw: ruleWeights - весовые правила, результаты вычислений
        :param fr: function result - результат вычисления функций
        :return: значения выходных функций
        """
        numerator: Dict[SugenoVariable, float] = defaultdict(float)
        denominator: Dict[SugenoVariable, float] = defaultdict(float)
        for out in self.out:
            numerator[out] = .0
            denominator[out] = .0

        for rule, weight in rw.items():
            variable: SugenoVariable = rule.conclusion.variable
            z: float = fr[variable][rule.conclusion.term]
            numerator[variable] += z * weight
            denominator[variable] += weight

        return {out: .0 if denominator[out] == .0 else numerator[out] / denominator[out] for out in self.out}

    def calculate(self, input_values: Dict[FuzzyVariable, float]) -> Dict[SugenoVariable, float]:
        if len(self.rules) == 0:
            raise Exception('Должно быть как минимум одно правило')
        fi: Dict[FuzzyVariable, Dict[Term, float]] = self.fuzzify(input_values)     # Шаг фаззификации
        rw: Dict[FuzzyRule, float] = self.evaluate_conditions(fi)                   # Агрегация подусловий
        fr: Dict[SugenoVariable, Dict[SugenoFunction, float]] = self.evaluate_functions(input_values)
        result: Dict[SugenoVariable, float] = self.combine_result(rw, fr)
        return result
