import typing as t

SAME_FACTOR = 3
SPIKE_FACTOR = 40

def _check_for_spike(beginning, middle, end):
    _, y_begin = beginning
    _, y_end = end
    _, y_middle = middle

    y_mean = (y_begin + y_end) / 2
    if abs(y_end - y_begin) < SAME_FACTOR:
        return abs(y_middle - y_mean) > SPIKE_FACTOR
    return False

    # return abs(y_middle - y_mean) / y_mean > SPIKE_FACTOR


class Smoother:

    def __init__(self):
        self.buffered = (None, None)
        self.callbacks = []

    def register_callback(self, cb: t.Callable):
        self.callbacks.append(cb)

    def _call_all(self, *args):
        for c in self.callbacks:
            c(args)

    def receive_item(self, ts, value):
        first_buffered, second_buffered = self.buffered
        if first_buffered is None:
            self.buffered = ((ts, value), None)
        elif second_buffered is None:
            self.buffered = (first_buffered, (ts, value))
            self._call_all(*first_buffered)
        else:
            if _check_for_spike(first_buffered, second_buffered, (ts, value)):
                print("Spike detected!:", first_buffered, second_buffered, (ts, value))
                second_buffered = (second_buffered[0], (first_buffered[1] + value) / 2)
            self.buffered = (second_buffered, (ts, value))
            self._call_all(*second_buffered)





