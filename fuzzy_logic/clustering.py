"""
Luferov Victor <lyferov@yandex.ru>

SubtractClustesing - горная кластеризация
"""

from typing import List, Tuple
import numpy as np


class SubtractClustering:
    """
    Горная кластеризация, все данные приводят к единичному гиперкубу
    """

    def __init__(self, x: np.ndarray, radii: np.ndarray, sf: float = 1.25, ar: float = .5, rr: float = .15):
        """
        Конструктор создания горной кластеризации
        :param x: матрица входных данных
        :param radii: радиус класетров
        :param sf: sqshFactor - коэффициент подавления
        :param ar: acceptRatio - коэффициент принятия
        :param rr: rejectRatio - коэффициент отторжения
        """
        self.x: np.ndarray = x
        self.radii: np.ndarray = radii
        self.sf: float = sf
        self.ar: float = ar
        self.rr: float = rr

    def __call__(self, *args, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Запускаем алгоритм горной кластеризации
        :return: centers, sigmas
        """
        num_params, num_points = self.x.shape   # Количество столбцов, количетсво строк
        accum_multp: np.ndarray = 1. / self.radii
        sqsh_multp: np.ndarray = 1 / (self.radii * self.sf)
        # Находим максимальное значение
        min_x: np.ndarray = self.x.min(axis=1)
        max_x: np.ndarray = self.x.max(axis=1)
        # Нормализуем данные, приводим к единичному гиперкубу
        x: np.ndarray = (self.x - min_x[:, np.newaxis]) / (max_x - min_x)[:, np.newaxis]
        # Ограничиваем от 0 до 1
        x[x > 1] = 1.
        x[x < 0] = .0
        # Вычисляем потенциал точек
        potential_values: np.ndarray = np.zeros([num_points])
        for j in range(num_points):
            point: np.ndarray = x[:, j]
            dx: np.ndarray = (point[:, np.newaxis] - x) * accum_multp[:, np.newaxis]
            potential_values[j] = np.sum([
                np.exp(-4. * np.sum([
                    dx[k, i] ** 2 for k in range(num_params)
                ])) for i in range(num_points)
            ])
        num_clusters: int = 0                                   # Количество кластеров
        max_potential: np.ndarray = potential_values.max()      # Точка с максимальным потенциалом
        ref_max_potential: np.ndarray = max_potential           # Самый большой максимальный мотенциал
        max_potential_index: int = potential_values.argmax()    # Индекс максимального потенциала
        centers: List[np.ndarray] = []                          # Центры кластеров
        find_more: int = 1                                      # Флаг поиска центров класетров
        while find_more != 0 and max_potential != 0:
            find_more: int = 0
            max_point: np.ndarray = x[:, max_potential_index]
            max_potential_ratio: np.ndarray = max_potential / ref_max_potential
            if max_potential_ratio > self.ar:                   # Новое значение пика является значительным
                find_more: int = 1
            elif max_potential_ratio > self.rr:                 # Принято точку тогда, когда далеко от кластеров
                min_dest_sq = -1.
                for center in centers:
                    dx_sq: np.ndarray = np.sum([
                        np.power((max_point[i] - center[i]) * accum_multp[i], 2) for i in range(num_params)
                    ])
                    if min_dest_sq < 0 or dx_sq < min_dest_sq:
                        min_dest_sq = dx_sq
                    if max_potential_ratio + min_dest_sq ** .5 >= 1:
                        find_more = 1
                    else:
                        find_more = 2
            if find_more == 1:
                centers.append(max_point)
                num_clusters += 1
                dx: np.ndarray = (max_point[:, np.newaxis] - x) * sqsh_multp[:, np.newaxis]
                deduct: np.ndarray = np.array([
                    max_potential * np.exp(-4 * np.sum([
                        np.power(dx[i, j], 2) for i in range(num_params)
                    ])) for j in range(num_points)
                ])
                potential_values -= deduct
                potential_values[potential_values < 0] = 0
                max_potential: np.ndarray = potential_values.max()
                max_potential_index: int = potential_values.argmax()
            elif find_more == 2:
                potential_values[max_potential_index] = .0
                max_potential: np.ndarray = potential_values.max()
                max_potential_index: int = potential_values.argmax()
        # Денормализация данных с использованием min_x and max_x
        centers: np.ndarray = (centers * (max_x - min_x) + min_x).transpose()
        sigmas: np.ndarray = (self.radii * (max_x - min_x)) / 8 ** .5
        return centers, sigmas
