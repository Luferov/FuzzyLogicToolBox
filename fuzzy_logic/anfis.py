import numpy as np
from typing import Dict, List
from collections import defaultdict
from .sugeno_fs import SugenoFuzzySystem
from .rules import FuzzyRule
from .rule_parser import RuleParser
from .variables import FuzzyVariable, SugenoVariable, SugenoFunction
from .terms import Term
from .types import AndMethod, OrMethod


class Anfis(SugenoFuzzySystem):

    name_input: str = 'input'           # Имена входных переменных
    name_output: str = 'output1'        # Имя выходной переменной
    name_mf: str = 'mf'                 # Имена лингвистических термов

    def __init__(self,
                 x: np.ndarray,                     # Вектор входа
                 y: np.ndarray,                     # Вектор выхода
                 radii: float = .5,                 # Радиус кластеров
                 sf: float = 1.25,                  # Коэффициент принятия
                 ar: float = .5,                    # Коэффициент принятия
                 rr: float = .15):                  # Коэффициент отторжения
        super().__init__()
        # Обучающая выборка
        self.x: np.ndarray = x
        self.y: np.ndarray = y
        # Переменные кластеризации
        self.__radii: float = radii
        self.__sqsh_factor: float = sf
        self.__accept_ratio: float = ar
        self.__reject_ratio: float = rr
        # Переменные обучения
        self.__error = .0                           # Желательная ошибка при обучении
        self.__epochs = 10                          # Количество эпох обучения
        self.__errors_train: List[float] = []       # Ошибки при обучении на каждой эпохе
        self.__nu: float = .1                       # Коэффициент обучения
        self.__nu_step: float = .9                  # Изменение nu на каждом шаге
        self.__rules_text: List[str] = []           # Текстовое представление правил






