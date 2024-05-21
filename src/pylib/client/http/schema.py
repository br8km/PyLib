"""HTTP Client Schema."""

from dataclasses import dataclass
from pathlib import Path

import arrow

from ...storage.cache import MemoryCache
from ...utils.debugger import Debugger
from ...utils.timer import Delayer


__all__ = [
    "DebugRequest",
    "DebugResponse",
    "DebugData",
    "HTTPDebugger",
    "HTTPDelayer",
    "RateLimit",
]


@dataclass
class AbsDebugItem:
    """Abstract cls for DebugItem."""

    time_stamp: float

    url: str

    headers: dict
    cookies: dict

    @property
    def time_str(self) -> str:
        """Convert time_stamp from float to string."""
        return arrow.get(self.time_stamp).format()


@dataclass
class DebugRequest(AbsDebugItem):
    """Request Data for Debugger."""

    method: str

    params: dict


@dataclass
class DebugResponse(AbsDebugItem):
    """Response Data for Debugger."""

    success: bool
    code: int

    text: str
    json: dict


@dataclass
class DebugData:
    """Data for Debugger."""

    req: DebugRequest
    res: DebugResponse


class HTTPDebugger(Debugger):
    """HTTP Debugger."""

    _data: DebugData

    def __init__(
        self,
        name: str,
        dir: Path,
        length: int = 6,
        seperator: str = "-",
    ) -> None:
        super().__init__(
            name=name,
            dir=dir,
            length=length,
            seperator=seperator,
        )
        self._data = DebugData(
            req=DebugRequest(
                time_stamp=0,
                url="",
                headers={},
                cookies={},
                method="",
                params={},
            ),
            res=DebugResponse(
                time_stamp=0,
                url="",
                headers={},
                cookies={},
                success=False,
                code=0,
                text="",
                json={},
            ),
        )


class HTTPDelayer(Delayer):
    """HTTP Delayer with MemoryCache as errors data storage."""

    _errors: MemoryCache

    def __init__(self, seconds: int = 3600 * 24) -> None:
        super().__init__()
        self._errors = MemoryCache(seconds=seconds)


@dataclass
class RateLimit:
    """RateLimit Headers."""

    limit: int
    ramining: int
    reset: int
