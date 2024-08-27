"""HTTP Abstract."""

from abc import abstractmethod
from typing import Optional

# This is the ONLY line different from other http client version
from curl_cffi.requests import Response

__all__ = [
    "AbsHTTP",
]


class AbsHTTP:
    """Abstract cls for HTTP Client."""

    @abstractmethod
    def req(self) -> Optional[Response]:
        """HTTP Request Method."""
        raise NotImplementedError

    @abstractmethod
    def get(self) -> Optional[Response]:
        """HTTP GET Method."""
        raise NotImplementedError

    @abstractmethod
    def head(self) -> Optional[Response]:
        """HTTP HEAD Method."""
        raise NotImplementedError

    @abstractmethod
    def post(self) -> Optional[Response]:
        """HTTP POST Method."""
        raise NotImplementedError

    @abstractmethod
    def put(self) -> Optional[Response]:
        """HTTP PUT Method."""
        raise NotImplementedError

    @abstractmethod
    def patch(self) -> Optional[Response]:
        """HTTP PATCH Method."""
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> Optional[Response]:
        """HTTP DELETE Method."""
        raise NotImplementedError

    @abstractmethod
    def options(self) -> Optional[Response]:
        """HTTP OPTIONS Method."""
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> Optional[Response]:
        """Decrepatched. HTTP CONNECT Method."""
        raise NotImplementedError
