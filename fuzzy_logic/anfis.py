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

    @property
    def radii(self) -> float:
        """
        :return: Радиус кластеров
        """
        return self.__radii

    @radii.setter
    def radii(self, value):
        if value < 0:
            raise Exception(f'Значение radii не может быть меньше 0')
        self.__radii = value

    @property
    def sqsh_factor(self) -> float:
        """
        :return: Коэффициент подавления
        """
        return self.__sqsh_factor

    @sqsh_factor.setter
    def sqsh_factor(self, value):
        if value < 0:
            raise Exception(f'Значение sqsh_factor не может быть меньше 0')
        self.__sqsh_factor = value

    @property
    def reject_ratio(self) -> float:
        """
        :return: Коэффициент принятия
        """
        return self.__accept_ratio

    @reject_ratio.setter
    def reject_ratio(self, value):
        """
        :param value: Коэффициент отторжения
        :return:
        """
        if value < 0:
            raise Exception(f'Значение reject_ratio не может быть меньше 0')
        self.__reject_ratio = value

    @property
    def nu(self) -> float:
        """
        :return: получение коэффициента обучения
        """
        return self.__nu

    @nu.setter
    def nu(self, value):
        """
        :param value: значение коэффициента обучения
        :return:
        """
        if not 0 < value < 1:
            raise Exception(f'Значение должны быть в пределах 0 < {value} < 1')
        self.__nu = value

    @property
    def epochs(self) -> float:
        """
        :return: получение эпох для получения
        """
        return self.__epochs

    @epochs.setter
    def epochs(self, value):
        if value < 0:
            raise Exception(f'Значение не может быть меньше 0')
        self.__epochs = value

    @property
    def errors_train(self) -> List[float]:
        """
        :return: Ошибка при обучении Anfis
        """
        return self.__errors_train

    def calculate(self, x: np.ndarray) -> Dict[SugenoVariable, float]:
        """
        Рассчитываем значение anfis
        :param x: вектор входных значений
        :return:
        """

        pass

    def train(self):
        """
        Обучаем Anifs
        :return:
        """

        pass

    def generate(self):
        """
        Генерируем anfis
        :return:
        """
        pass

    def __set_coefficient(self, c: np.ndarray):
        pass
