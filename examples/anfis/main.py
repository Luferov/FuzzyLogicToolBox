import numpy as np
from pprint import pprint
from fuzzy_logic.anfis import Anfis

x: np.ndarray = np.array([
    [.1, .3, .5, .7, .9],
    [.1, .2, .4, .6, .8]
])

y: np.ndarray = np.array([.01, .06, .2, .42,  .72])

anfis: Anfis = Anfis(x, y, .5)
anfis.train()
pprint(f'{anfis.calculate([.2, .3])} == {.2 * .3}')
