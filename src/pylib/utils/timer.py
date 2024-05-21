"""Time Operation."""

import random
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

import arrow
import pytz
from arrow import Arrow

__all__ = [
    "timing",
    "Timer",
    "Delayer",
]


def timing(func: Callable) -> Any:
    """Measure Timing of functions.

    :Usage Example:

    @timing
    def hello(name: str, age: int) -> None:
        return f'Hello {name}, You are {age} years old now!'

    """

    @wraps(func)
    def wrap(*args: Any, **kwargs: Any) -> Any:
        """Wrap function."""
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(
            "func:%r args:%r, kwargs:%r took: %2.8f sec"
            % (func.__name__, args, kwargs, end - start)
        )

        return result

    return wrap


class Timer:
    """Base cls for time transformation and smart Delaying."""

    def __init__(self, tz_info: str = "Asia/Hong_Kong") -> None:
        """Init Timer."""
        self._tz_info: str = tz_info
        self._tz_offset: float = self.utc_offset(tz_info)

        self._now: Arrow = self.to_now()
        self._fmt: str = "YYYY-MM-DD HH:mm:ssZZ"

    def to_now(self) -> Arrow:
        """Get now `Arrow` object."""
        # return arrow.utcnow().shift(seconds=self._tz_offset)
        return arrow.utcnow().to(tz=self._tz_info)

    def to_str(self, now: Optional[Arrow] = None, fmt: str = "") -> str:
        """string format for now"""
        fmt = fmt if fmt else self._fmt
        now = now if now else self._now
        return now.format(fmt)

    def to_int(self, now: Optional[Arrow] = None) -> int:
        """int timestamp for now"""
        now = now if now else self._now
        return int(now.utcnow().timestamp())

    def int2str(
        self,
        now_ts: int,
        tzinfo: str = "",
        fmt: str = "",
    ) -> str:
        """int to string for timestamp of now"""
        fmt = fmt if fmt else self._fmt
        tzinfo = tzinfo if tzinfo else self._tz_info
        return arrow.get(now_ts, tzinfo=tzinfo).format(fmt)

    def str2int(self, now_str: str, fmt: str = "", tzinfo: str = "") -> int:
        """string to int for timestamp of now"""
        fmt = fmt if fmt else self._fmt
        tzinfo = tzinfo if tzinfo else self._tz_info
        return int(arrow.get(now_str, fmt, tzinfo=tzinfo).timestamp())

    def iso_week(self, offset: int = 0) -> str:
        """return ISO week format like: `2020W36`"""
        iso = self._now.shift(weeks=offset).isocalendar()
        return "{}W{}".format(iso[0], iso[1])

    @classmethod
    def utc_offset(cls, time_zone: str) -> float:
        """Convert time zone string to utc offset."""
        now = datetime.now(pytz.timezone(time_zone))
        offset = now.utcoffset()
        if offset:
            return offset.total_seconds()
        return 0.0


class Delayer:
    """Delayer."""

    @classmethod
    def between(cls, min: float, max: float, debug: bool = False) -> float:
        """Delay Between (min, max) seconds. skip REAL sleep if debug is True."""
        pause = random.uniform(min, max)
        if not debug:
            time.sleep(pause)
        return pause

    @classmethod
    def near(cls, base: float, percentage: float, debug: bool = False) -> float:
        """Delay Near (base - percentage, base + percentage) seconds."""
        assert 0 < percentage < 1
        return cls.between(
            min=base - base * percentage,
            max=base + base * percentage,
            debug=debug,
        )

    @classmethod
    def more_than(cls, base: float, percentage: float, debug: bool = False) -> float:
        """Delay More than (base, base + percentage) seconds."""
        assert 0 < percentage < 1
        return cls.between(
            min=base,
            max=base + base * percentage,
            debug=debug,
        )

    @classmethod
    def less_than(cls, base: float, percentage: float, debug: bool = False) -> float:
        """Delay Less than (base - percentage, base) seconds."""
        assert 0 < percentage < 1
        return cls.between(
            min=base - base * percentage,
            max=base,
            debug=debug,
        )

    @classmethod
    def backoff(
        cls,
        base: float = 1.0,
        factor: int = 2,
        errors: int = 0,
        percentage: float = 0.1,
        debug: bool = False,
    ) -> float:
        """Delay with Exponential backoff.

        Reference:
            - https://github.com/litl/backoff

        Parameters:
            :base:float, base seconds for calculate pause time;
            :factor:int, backoff factor;
            :errors:int, number of errors occured in a period of time;
            :percentage:float, ratio to base float for calculate pause seconds;
            :debug:bool, Default `False`, skip REAL sleep if True;

        Returns:
            :float, seconds of time pause;

        """
        factor = max(factor, 2)
        exponent = factor * (2**errors) if errors else factor
        return cls.more_than(
            base=base * exponent,
            percentage=percentage,
            debug=debug,
        )

