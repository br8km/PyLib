import string

import regex as re

from pylib.alter.chars import str_rnd, hash2b, hash2s


class Tester:
    """TestCase for chars operation."""

    length: int = 12
    times: int = 100

    def test_str_rnd(self) -> None:
        """Test string random generation."""

        assert all(
            len(x) == self.length and re.compile(r"[A-Z]").findall(x) == []
            for x in (str_rnd(number=self.length) for _ in range(100))
        )

        assert any(
            re.compile(r"[A-Z]").findall(str_rnd(upper=True)) != [] for _ in range(self.times)
        )

        strong_chars = "@#$%"
        assert any(
            char in str_rnd(strong=True) for char in strong_chars for _ in range(self.times)
        )

        assert any(
            char in str_rnd(ultra=True)
            for char in string.punctuation
            for _ in range(self.times)
        )

    def test_hash_str(self) -> None:
        """Test hash string."""
        hash_set = set()
        for _ in range(self.times):
            strs = str_rnd(number=self.length, upper=True, strong=True, ultra=True)
            hash_str = hash2s(strs)
            assert hash_str and hash_str not in hash_set
            hash_set.add(hash_str)

    def test_hash_bytes(self) -> None:
        """Test hash bytes."""
        hash_set = set()
        for _ in range(self.times):
            strs = str_rnd(number=self.length, upper=True, strong=True, ultra=True)
            hash_bytes = hash2b(strs)
            assert hash_bytes and hash_bytes not in hash_set
            hash_set.add(hash_bytes)
