"""HTTP Basic Client."""

from pathlib import Path
from typing import Any, Optional

import arrow
from requests import Response, Session
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    JSONDecodeError,
    ProxyError,
    ReadTimeout,
    SSLError,
)

from .abs import AbsHTTP
from ...storage.io import IO

__all__ = [
    "HTTPBasic",
]


class HTTPBasic(AbsHTTP):
    """HTTP Basic Client, for Fast Operation with Prototype.

    Features:
        - Custom Headers Operation
        - Cookies Operation
        - Flexible Request Parameters

    """

    _user_agent: str
    _proxy_url: str
    _timeout: int
    _silent: bool
    _session: Session

    def __init__(
        self,
        user_agent: str = "",
        proxy_url: str = "",
        timeout: int = 30,
        silent: bool = False,
    ) -> None:
        """Init HTTP Basic Client.

        :Parameters:
            :user_agent:str, HTTP Header for `User-Agent`;
            :proxy_url:str, constitute HTTP session proxies if present.
            :time_out:int, HTTP Request timeout, Default 30 seconds.
            :silent:bool, print realtime info on request if Not silent.

        """
        self._user_agent = user_agent
        self._proxy_url = proxy_url
        self._timeout = timeout
        self._silent = silent

        self._session = Session()

        if user_agent:
            self._session.headers.update(
                {
                    "User-Agent": user_agent,
                }
            )

        if proxy_url:
            # Only HTTP|Socks5 Proxy Supported
            if not (
                proxy_url.startswith("http")
                or proxy_url.startswith("socks5")
            ):
                raise ValueError("Proxy Scheme Error!")

            self._session.proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

    def header_set(self, key: str, value: Optional[str]) -> None:
        """Set session header value with key string."""
        if value is not None:
            self._session.headers[key] = value
        else:
            if key in self._session.headers.keys():
                del self._session.headers[key]

    def header_get(self, key: str) -> str:
        """Get session header value by key string."""
        if key and key in self._session.headers.keys():
            value = self._session.headers[key]
            if value:
                return value
        return ""

    def set_hd_accept(self, value: str = "*/*") -> None:
        """Shortcut for set heaer `Accept`."""
        self.header_set("Accept", value)

    def set_hd_accept_encoding(self, value: str = "gzip, defalte, br") -> None:
        """Shortcut for Set header `Accept-Encoding`."""
        self.header_set("Accept-Encoding", value)

    def set_hd_accept_lang(self, value: str = "en-US,en;q=0.5") -> None:
        """Shortcut for Set header `Accept-Language`."""
        self.header_set("Accept-Language", value)

    def set_hd_origin(self, value: Optional[str]) -> None:
        """Shortcut for Set header `Origin`."""
        self.header_set("Origin", value)

    def set_hd_referer(self, value: Optional[str]) -> None:
        """Shortcut for Set header `Referer`."""
        self.header_set("Referer", value)

    def set_hd_content_type(self, value: Optional[str]) -> None:
        """Shortcut for Set header `Content-Type`."""
        self.header_set("Content-Type", value)

    def set_hd_ajax(self, value: str = "XMLHttpRequest") -> None:
        """Shortcut for Set header `X-Requested-With`."""
        self.header_set("X-Requested-With", value)

    def set_hd_form_data(self, utf8: bool = True) -> None:
        """Shortcut for Set header `Content-Type` for form data submit."""
        value = "application/x-www-form-urlencoded"
        if utf8 is True:
            value = f"{value}; charset=UTF-8"
        self.header_set("Content-Type", value)

    def set_hd_json_payload(self, utf8: bool = True) -> None:
        """Shortcut for Set header `Content-Type` for json payload post."""
        value = "application/json"
        if utf8 is True:
            value = f"{value}; charset=UTF-8"
        self.header_set("Content-Type", value)

    def cookie_set(self, key: str, value: Optional[str]) -> None:
        """Set cookie for session."""
        return self._session.cookies.set(key, value)

    def cookie_get(self, key: str) -> Optional[str]:
        """Set cookie for session."""
        return self._session.cookies.get(name=key)

    def cookie_load(self, file_cookie: Path) -> None:
        """Load session cookie from local file."""
        if file_cookie.is_file():
            self._session.cookies.update(IO.load_dict(file_cookie))

    def cookie_save(self, file_cookie: Path) -> None:
        """Save session cookies into local file."""
        IO.save_dict(file_cookie, dict(self._session.cookies))

    def _prepare_headers(self, **kwargs: Any) -> None:
        """Preparing headers for following HTTP request."""
        if kwargs.get("json") is not None:
            self.set_hd_json_payload()
        elif kwargs.get("data") is not None:
            self.set_hd_form_data()

        headers = kwargs.get("headers")
        if headers is not None:
            for key, value in headers.items():
                self.header_set(key, value)

    def req(
        self,
        method: str,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """Perform HTTP Request."""

        self._prepare_headers(**kwargs)

        if not kwargs.get("timeout", None):
            kwargs["timeout"] = self._timeout

        try:
            response = self._session.request(method=method, url=url, **kwargs)
            if not self._silent:
                now = arrow.now().format()
                code = response.status_code
                length = len(response.text)
                message = f"{now} - [{code}]<{length}>{response.url}"
                print(message)

            return response

        except (
            ConnectionError,
            ConnectTimeout,
            HTTPError,
            JSONDecodeError,
            ProxyError,
            ReadTimeout,
            SSLError,
        ) as error:
            if debug:
                raise error

        return None

    def get(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP GET Method."""
        return self.req("GET", url, debug=debug, **kwargs)

    def head(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP HEAD Method."""
        return self.req("HEAD", url, debug=debug, **kwargs)

    def post(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP POST Method."""
        return self.req("POST", url, debug=debug, **kwargs)

    def put(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP PUT Method."""
        return self.req("PUT", url, debug=debug, **kwargs)

    def patch(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP PATCH Method."""
        return self.req("PATCH", url, debug=debug, **kwargs)

    def delete(
        self, url: str, debug: bool = False, **kwargs: Any
    ) -> Optional[Response]:
        """HTTP DELETE Method."""
        return self.req("DELETE", url, debug=debug, **kwargs)

    def options(
        self, url: str, debug: bool = False, **kwargs: Any
    ) -> Optional[Response]:
        """HTTP OPTIONS Method."""
        return self.req("OPTIONS", url, debug=debug, **kwargs)

    def connect(
        self, url: str, debug: bool = False, **kwargs: Any
    ) -> Optional[Response]:
        """Deprecated: HTTP CONNECT Method."""
        return self.req("CONNECT", url, debug=debug, **kwargs)

