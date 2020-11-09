import numpy as np
from typing import Dict, List
from .sugeno_fs import SugenoFuzzySystem
from .rules import FuzzyRule
from .variables import FuzzyVariable, SugenoVariable, LinearSugenoFunction
from .terms import Term
from .mf import NormalMF
from .clustering import SubtractClustering


class Anfis(SugenoFuzzySystem):
    name_input: str = 'input'  # Имена входных переменных
    name_output: str = 'output'  # Имя выходной переменной
    name_mf: str = 'mf'  # Имена лингвистических термов

    def __init__(self,
                 x: np.ndarray,  # Вектор входа
                 y: np.ndarray,  # Вектор выхода
                 radii: float = .5,  # Радиус кластеров
                 sf: float = 1.25,  # Коэффициент принятия
                 ar: float = .5,  # Коэффициент принятия
                 rr: float = .15):  # Коэффициент отторжения
        """

        :param x: Вектор входа [[], []]
        :param y: Вектор выхода []
        :param radii: Радиус кластеров
        :param sf: Коэффициент принятия
        :param ar: Коэффициент принятия
        :param rr: Коэффициент отторжения
        """
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
        self.__error = .0  # Желательная ошибка при обучении
        self.__epochs = 10  # Количество эпох обучения
        self.__errors_train: List[float] = []  # Ошибки при обучении на каждой эпохе
        self.__nu: float = .1  # Коэффициент обучения
        self.__nu_step: float = .9  # Изменение nu на каждом шаге
        self.__rules_text: List[str] = []  # Текстовое представление правил

    @property
    def rules_text(self) -> List[str]:
        return self.__rules_text

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
    def accept_ratio(self) -> float:
        return self.__accept_ratio

    @accept_ratio.setter
    def accept_ratio(self, value):
        self.__accept_ratio = value

    @property
    def reject_ratio(self) -> float:
        """
        :return: Коэффициент принятия
        """
        return self.__reject_ratio

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

    @property
    def count_input(self) -> int:
        """
        :return: Количество входных временных рядов
        """
        return self.x.shape[0]

    @property
    def count_output(self) -> int:
        """
        :return: Количество выходных точек
        """
        return self.y.shape[0]

    def calculate(self, x: List[float]) -> float:
        """
        Рассчитываем значение anfis
        :param x: вектор входных значений
        :return:
        """
        if len(x) != self.count_input:
            raise Exception(f'Количество входных значений и переменных разное: {len(x)} != {self.count_input}.')
        if len(self.inp) == 0:
            raise Exception('Нет входных переменных, возможно она не обучена.')
        return super() \
            .calculate({self.inp[i]: e for i, e in enumerate(x)})[self.output_by_name(f'{self.name_output}1')]

    def train(self):
        """
        Обучаем Anifs
        :return:
        """
        self.generate()
        if len(self.rules) == 0:
            raise Exception('Должно быть хотя бы одно нечеткое правило.')
        k: int = len(self.y)  # Количество параметров обучающей выборки
        l: int = (len(self.x) + 1) * len(self.rules)  # (m + 1) * n - количество входных переменных
        c: np.ndarray = np.array((l, 1))
        y: np.ndarray = np.array(self.y)  # Вектор столбец выходных данных
        self.__errors_train = []  # Обнуляем ошибку обучения
        for current_epoch in range(self.__epochs):
            # Формируем матрицу коэффициентов
            w: np.ndarray = np.zeros((k, l))
            ew: np.ndarray = np.zeros((k, len(self.rules)))
            for i in range(k):
                # Агрегирование подусловий
                rules_weight: Dict[FuzzyRule, float] = self.evaluate_conditions(
                    self.fuzzify({variable: self.x[j][i] for j, variable in enumerate(self.inp)})
                )
                ew[i, :] = np.array([*rules_weight.values()], float)
                beta: np.ndarray = ew[i, :] / sum(rules_weight.values())
                # Формируем входные переменные
                x: np.ndarray = np.ones(self.count_input + 1)  # +1, тк x0 = 1
                x[1:] = self.x[:, i]
                column_weight: int = 0
                for g in beta:  # перебираем по заключениям
                    for d in x:  # Перебираем по входным данным
                        w[i, column_weight] = g * d  # Перемножаем коэффициенты на переменные
                        column_weight += 1  # Увеличиваем строку на 1

            c = np.dot(np.linalg.pinv(w), y)
            y_hatch: np.ndarray = np.dot(w, c)  # Фактический выход сети
            # Правим коэффициенты
            for i, fv in enumerate(self.inp):
                for j, term in enumerate(fv.terms):
                    if not isinstance(term.mf, NormalMF):
                        # Пока что меняем только в том случае, если функция принадлежности колоколообразная
                        continue
                    mf: NormalMF = term.mf
                    # Перебираем все переменные, k - количество входных переменных
                    for g in range(k):
                        xa: float = self.x[i][g] - mf.b
                        yy_hatch = y_hatch[g] - self.y[g]  # y' - y
                        p: float = ew[g, j]
                        sp: float = sum(ew[g, :])
                        pb: float = p / (sp / mf.sigma ** 2)
                        # Инициализирум матрицы для нахождения C
                        x: np.ndarray = np.ones((self.count_input + 1))
                        x[1:] = self.x[:, g]
                        c_hatch: np.ndarray = np.ones((self.count_input + 1))
                        # Заполняем коэффициенты
                        start: int = j * (self.count_input + 1)
                        c_hatch[:] = c[start:start + (self.count_input + 1)]
                        cy: float = np.dot(x, c_hatch[:, np.newaxis])[0] - y_hatch[g]
                        mf.b -= 2 * self.nu * xa * yy_hatch * cy * pb  # Корректируем b
                        mf.sigma -= 2 * self.nu * (xa ** 2) * yy_hatch * cy * pb  # Корректируем sigma
            # Находим ошибку обучения на этапе
            self.__errors_train.append(sum(.5 * (y_hatch - self.y) ** 2))
        # Применяем параметры коэффициентов y = c0 + c1 * x1 + c2 * x2 + ... + ci * xi
        self.__set_coefficient(c)
        # Перезаписываем правила в силу ссылочного типа архитектуры
        self.rules = [self.parse_rule(rule) for rule in self.__rules_text]

    def generate(self):
        """
        Генерируем anfis
        :return:
        """
        x: np.ndarray = np.vstack((self.x, self.y))
        # Кластеризация данных
        centers, sigmas = SubtractClustering(
            x,
            np.array([self.radii for _ in range(x.shape[0])]),
            self.sqsh_factor,
            self.accept_ratio,
            self.reject_ratio
        )()
        # Разделяем на две части
        centers_in: np.ndarray = centers[:-1]
        centers_out: np.ndarray = centers[-1]
        sigmas_in: np.ndarray = sigmas[:-1]

        # Формируем входные переменные
        self.inp = [
            FuzzyVariable(
                f'{self.name_input}{i + 1}',
                np.min(self.x[i]),
                np.max(self.x[i]),
                *[
                    Term(f'{self.name_mf}{j + 1}', NormalMF(center, sigmas_in[i]))
                    for j, center in enumerate(center_in)
                ]
            ) for i, center_in in enumerate(centers_in)
        ]
        # Формируем выходные переменные нулевыми значениями
        self.out = [
            SugenoVariable(
                f'{self.name_output}1',
                *[
                    LinearSugenoFunction(
                        f'{self.name_mf}{j + 1}',
                        {variable: .0 for variable in self.inp},  # По умолчанию нулевые значения
                        center  # По умолчанию константа как центр
                    ) for j, center in enumerate(centers_out)
                ]
            )
        ]
        # Формируем нечеткую продукционную базу правил if (input1 is mf1) and (input2 is mf2) then (output1 is mf1)
        for i in range(centers_out.shape[0]):
            rule = 'if'
            for j in range(centers_in.shape[0]):
                rule += f' ({self.name_input}{j + 1} is {self.name_mf}{i + 1}) '
                if j != centers_in.shape[0] - 1:
                    rule += 'and'
            rule += f'then ({self.name_output}1 is {self.name_mf}{i + 1})'
            self.__rules_text.append(rule)
            self.rules.append(self.parse_rule(rule))

    def __set_coefficient(self, c: np.ndarray):
        """
        Устанавливаем функции принадлежности выходной переменной
        :param c: Матрица коэффициентов
        """
        for i, function in enumerate(self.output_by_name(f'{self.name_output}1').functions):
            if isinstance(function, LinearSugenoFunction):
                # Настройка фукнции принадлежности y = c0 + c1 * x1 + c2 * x2 + ... + ci * xi
                m: int = self.count_input + 1  # т.к. с0 <- +1
                start_position: int = i * m  # Позиция функции принадлежности в матрицы
                coefficients: np.ndarray = c[start_position: start_position + m]
                # Создаем новую функцию принадлежности
                self.output_by_name(f'{self.name_output}1').functions[i] = LinearSugenoFunction(
                    function.name,
                    {variable: coefficients[j + 1] for j, variable in enumerate(self.inp)},
                    coefficients[0]
                )
            else:
                raise Exception(f'Предусмотрено использование только LinearSugenoFunction в Anfis.')
