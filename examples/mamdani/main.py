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
