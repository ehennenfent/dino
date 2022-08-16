import typing as t


def extract_tail(buffer: t.Union[t.List, t.Deque], n: int) -> t.List:
    buf_len = len(buffer)
    return list(buffer[i] for i in range(max(0, buf_len - n), buf_len))
