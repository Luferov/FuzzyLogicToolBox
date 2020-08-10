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
