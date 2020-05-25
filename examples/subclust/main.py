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
pprint(sc.run())
