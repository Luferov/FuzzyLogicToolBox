# FuzzyLogic library
Authors: V.S. Luferov

## Fuzzy Variables

## Fuzzy Rules

## subtract clusteting
(Data for su/examples/subclust.m.csv)[/examples/subclust.m.csv]

```python
import numpy as np
from pprint import pprint
from fuzzy_logic.clustering import SubtractClustering
import csv


data = np.zeros([3, 600])
with open('m.csv') as f:
    spamreader = csv.reader(f, delimiter=',')
    for i, row in enumerate(spamreader):
        data[0, i] = float(row[0])
        data[1, i] = float(row[1])
        data[2, i] = float(row[2])

sc = SubtractClustering(data, np.array([0.6] * 3))
pprint(sc())
```

## Mamdani Fuzzy System

```python
from pprint import pprint
from fuzzy_logic.terms import Term
from fuzzy_logic.variables import FuzzyVariable
from fuzzy_logic.mamdani_fs import MamdaniFuzzySystem
from fuzzy_logic.mf import TriangularMF

t1 = Term('mf1', TriangularMF(0, 0, 0.5))
t2 = Term('mf2', TriangularMF(0, 0.5, 1))
t3 = Term('mf3', TriangularMF(0.5, 1, 1))
input1: FuzzyVariable = FuzzyVariable('input1', 0, 1, t1, t2, t3)
input2: FuzzyVariable = FuzzyVariable(
    'input2', 0, 1,
    Term('mf1', TriangularMF(0, 0, 0.5)),
    Term('mf2', TriangularMF(0, 0.5, 1)),
    Term('mf3', TriangularMF(0.5, 1, 1))
)
output = FuzzyVariable(
    'output', 0, 1,
    Term('mf1', TriangularMF(0, 0, 0.5)),
    Term('mf2', TriangularMF(0, 0.5, 1)),
    Term('mf3', TriangularMF(0.5, 1, 1))
)

mf: MamdaniFuzzySystem = MamdaniFuzzySystem([input1, input2], [output])
mf.rules.append(mf.parse_rule('if (input1 is mf1) and (input2 is mf1) then (output is mf1)'))
mf.rules.append(mf.parse_rule('if (input1 is mf2) and (input2 is mf2) then (output is mf2)'))
result = mf.calculate({input1: 0.45, input2: 0.45})
pprint(result)

```
## Sugeno Fuzzy System

```python
from pprint import pprint
from fuzzy_logic.terms import Term
from fuzzy_logic.variables import FuzzyVariable, SugenoVariable, LinearSugenoFunction
from fuzzy_logic.sugeno_fs import SugenoFuzzySystem
from fuzzy_logic.mf import TriangularMF

t1: Term = Term('mf1', TriangularMF(0, 0, 0.5))
t2: Term = Term('mf2', TriangularMF(0, 0.5, 1))
t3: Term = Term('mf3', TriangularMF(0.5, 1, 1))

input1: FuzzyVariable = FuzzyVariable('input1', 0, 1, t1, t2, t3)
input2: FuzzyVariable = FuzzyVariable(
    'input2', 0, 1,
    Term('mf1', TriangularMF(0, 0, 0.5)),
    Term('mf2', TriangularMF(0, 0.5, 1)),
    Term('mf3', TriangularMF(0.5, 1, 1))
)
output: SugenoVariable = SugenoVariable(
    'output',
    LinearSugenoFunction('mf1', {input1: 0.1, input2: 0.3}, 0.5),
    LinearSugenoFunction('mf2', {input1: 0.4, input2: 0.2}, 0.7)
)

mf: SugenoFuzzySystem = SugenoFuzzySystem([input1, input2], [output])
mf.rules.append(mf.parse_rule('if (input1 is mf1) and (input2 is mf1) then (output is mf1)'))
mf.rules.append(mf.parse_rule('if (input1 is mf2) and (input2 is mf2) then (output is mf2)'))
result = mf.calculate({input1: 0.45, input2: 0.45})
pprint(result)

```
## Anfis

```python
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

```


