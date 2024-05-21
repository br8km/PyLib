import time

from pylib.utils.timer import Delayer, Timer, timing


class Tester:
    """TestCase for Timer/Delayer."""

    tz_info = "Asia/Hong_Kong"
    tz_offset = float(8 * 3600)

    timer = Timer(tz_info=tz_info)

    @timing
    def _method_with_delay(self, name: str, pause: float) -> float:
        """Delay for pause, return pause."""
        print(f"name = {name}")
        time.sleep(pause)
        return pause

    def test_timing(self) -> None:
        """Test timing decorator."""
        name = "Andy"
        pause = 0.5
        assert pause == self._method_with_delay(name, pause=pause)

    def test_utc_offset(self) -> None:
        """Test UTC offset"""
        offset = self.timer.utc_offset(self.tz_info)
        print(f"offset = {offset}")
        assert offset == self.tz_offset

    def test_transforming(self) -> None:
        """Test timer cls."""
        # Must Be New Timer Object, otherwise timer._now not correct
        self.timer = Timer(tz_info=self.tz_info)

        now_ts = self.timer.to_int()
        print(f"now_ts = {now_ts}")
        now_str = self.timer.to_str()
        print(f"now_str = {now_str}")

        for index in range(3):
            time.sleep(0.5)
            new_ts = self.timer.str2int(now_str=now_str)
            print(f"[{index}]new_ts = {new_ts}")
            assert now_ts == new_ts

        for index in range(3):
            time.sleep(0.5)
            new_str = self.timer.int2str(now_ts=now_ts)
            print(f"[{index}]new_str = {new_str}")
            assert now_str == new_str

        week = self.timer.iso_week()
        assert "W" in week
        assert week.startswith("W") is False
        assert week.endswith("W") is False

    def test_delay(self) -> None:
        """Test delay methods."""
        delayer = Delayer()
        # Delay Between
        left, right = 1.0, 3.0
        pause = delayer.between(min=left, max=right, debug=True)
        assert left < pause < right

        # Delay Near
        base = 10.0
        percentage = 0.05
        pause = delayer.near(base=base, percentage=percentage, debug=True)
        assert abs(pause - base) < base * percentage

        # Delay More Than
        base = 10.0
        percentage = 0.05
        pause = delayer.more_than(base=base, percentage=percentage, debug=True)
        assert bool(abs(pause - base) < base * percentage and pause > base)

        # Delay Less Than
        base = 10.0
        percentage = 0.05
        pause = delayer.less_than(base=base, percentage=percentage, debug=True)
        assert bool(abs(pause - base) < base * percentage and pause < base)

        # Delay Backoff
        base = 10.0
        percentage = 0.05
        pause = 0
        for errors in range(10):
            next = delayer.backoff(
                base=base,
                factor=2,
                errors=errors,
                percentage=percentage,
                debug=True,
            )
            assert next > pause
            pause = next

        # Delay debug = False
        start = time.time()
        pause = delayer.between(1, 2, debug=False)
        print(f"real.pause = {pause}")
        assert time.time() >= start + pause
