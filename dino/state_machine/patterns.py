from functools import partial


def ne_thresh(threshold: float, a, b):
    return abs(a - b) / b > threshold


def eq_thresh(threshold: float, a, b):
    return abs(a - b) / b < threshold


eq_1p = partial(eq_thresh, 0.01)
eq_5p = partial(eq_thresh, 0.05)
eq_10p = partial(eq_thresh, 0.1)
eq_20p = partial(eq_thresh, 0.2)

ne_1p = partial(ne_thresh, 0.01)
ne_5p = partial(ne_thresh, 0.05)
ne_10p = partial(ne_thresh, 0.1)
ne_20p = partial(ne_thresh, 0.2)
