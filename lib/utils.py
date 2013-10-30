import numpy as np


def percentile90(x):
    return np.percentile(x, 90)


def trend(row):
    if row[0] > row[1]:
        return (row[0] / row[1]) * 100 - 100
    else:
        return -((row[1] / row[0]) * 100 - 100)

