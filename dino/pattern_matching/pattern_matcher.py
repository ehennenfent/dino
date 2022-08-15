import typing as t
import unittest
from dataclasses import dataclass, field
from operator import gt, lt


def _extract_tail(buffer: t.Union[t.List, t.Deque], n: int) -> t.List:
    buf_len = len(buffer)
    # TODO: REMOVE [1] BECAUSE THIS SHOULDN'T REQUIRE TUPLES
    return list(buffer[i][1] for i in range(max(0, buf_len - n), buf_len))


@dataclass
class PatternMatcher:
    patterns: t.Dict[str, t.Tuple[t.Tuple, t.Callable]] = field(default_factory=dict)

    def register_pattern(self, name: str, pattern: t.Tuple, callback: t.Callable):
        self.patterns[name] = (pattern, callback)

    def match(self, data: t.Union[t.Deque, t.List]):
        for pattern, callback in self.patterns.values():
            if self._match_pattern(_extract_tail(data, len(pattern) + 1), pattern):
                callback()

    @staticmethod
    def _match_pattern(data, pattern) -> bool:
        if len(data) <= len(pattern):
            return False
        return all(
            comparator(data[i + 1], data[i])
            for i, (comparator, _) in enumerate(zip(pattern, data))
        )


class TestPatternMatcher(unittest.TestCase):
    def setUp(self) -> None:
        self.matcher = PatternMatcher()
        self.matched = False

        def set_matched():
            self.matched = True

        self.matcher.register_pattern("up_up_down", (gt, gt, lt), set_matched)

    def test_match(self):
        self.matcher.match([20, 30, 40, 30])
        self.assertTrue(self.matched)

    def test_no_match(self):
        self.matcher.match([20, 30, 40, 40])
        self.assertFalse(self.matched)

    def test_extra_data_match(self):
        self.matcher.match([0, 10, 20, 30, 40, 30])
        self.assertTrue(self.matched)

    def test_extra_data_no_match(self):
        self.matcher.match([0, 10, 20, 30, 40, 40])
        self.assertFalse(self.matched)

    def test_match_not_at_end(self):
        self.matcher.match([20, 30, 40, 30, 20, 20])
        self.assertFalse(self.matched)

    def test_data_too_short(self):
        self.matcher.match([20, 30, 40])
        self.assertFalse(self.matched)


if __name__ == "__main__":
    unittest.main()
