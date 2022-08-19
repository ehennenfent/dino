from functools import partial, reduce
import operator


def anything(_a, _b):
    return True


def _chain(comparators, *args):
    return reduce(operator.and_, (c(*args) for c in comparators))


def positive(a, b):
    return a > 0 and b > 0


def negative(a, b):
    return a < 0 and b < 0


def _arbitrary_comparison_thresh(comparator, threshold, a, b):
    return comparator(a, b) and ne_thresh(threshold, a, b)


def ne_thresh(threshold: float, a, b):
    return abs(a - b) / max(b, .000001) > threshold


def eq_thresh(threshold: float, a, b):
    return abs(a - b) / max(b, .000001) < threshold


gt_thresh = partial(_arbitrary_comparison_thresh, operator.gt)
lt_thresh = partial(_arbitrary_comparison_thresh, operator.lt)

eq_1p = partial(eq_thresh, 0.01)
eq_5p = partial(eq_thresh, 0.05)
eq_10p = partial(eq_thresh, 0.1)
eq_20p = partial(eq_thresh, 0.2)

ne_1p = partial(ne_thresh, 0.01)
ne_5p = partial(ne_thresh, 0.05)
ne_10p = partial(ne_thresh, 0.1)
ne_20p = partial(ne_thresh, 0.2)

gt_pos_1p = partial(_chain, [partial(gt_thresh, 0.01), positive])
gt_pos_5p = partial(_chain, [partial(gt_thresh, 0.05), positive])
gt_pos_10p = partial(_chain, [partial(gt_thresh, 0.1), positive])
gt_pos_20p = partial(_chain, [partial(gt_thresh, 0.2), positive])

gt_neg_1p = partial(_chain, [partial(gt_thresh, 0.01), negative])
gt_neg_5p = partial(_chain, [partial(gt_thresh, 0.05), negative])
gt_neg_10p = partial(_chain, [partial(gt_thresh, 0.1), negative])
gt_neg_20p = partial(_chain, [partial(gt_thresh, 0.2), negative])

lt_pos_1p = partial(_chain, [partial(lt_thresh, 0.01), positive])
lt_pos_5p = partial(_chain, [partial(lt_thresh, 0.05), positive])
lt_pos_10p = partial(_chain, [partial(lt_thresh, 0.1), positive])
lt_pos_20p = partial(_chain, [partial(lt_thresh, 0.2), positive])

lt_neg_1p = partial(_chain, [partial(lt_thresh, 0.01), negative])
lt_neg_5p = partial(_chain, [partial(lt_thresh, 0.05), negative])
lt_neg_10p = partial(_chain, [partial(lt_thresh, 0.1), negative])
lt_neg_20p = partial(_chain, [partial(lt_thresh, 0.2), negative])
