"""HTTP Basic Client."""
import sys

import asyncio
from pathlib import Path
from typing import Any, Optional, Union

import arrow
from curl_cffi.requests import AsyncSession, BrowserType, Response, Session
from curl_cffi.requests.errors import RequestsError

from ...storage.io import IO
from .abs import AbsHTTP

if sys.platform:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class HTTPBase(AbsHTTP):
    """Abstract HTTP Client Base."""

    _user_agent: str
    _proxy_url: str
    _proxies: dict[str, str]

    _silent: bool
    _timeout: int

    _session: Union[Session, AsyncSession]

    def __init__(
        self,
        impersonate: str = "chrome",
        proxy_url: str = "",
        silent: bool = False,
        timeout: int = 30,
    ) -> None:
        """Init HTTP Basic Client.

        :Parameters:
            :impersonate:str, Browser Types to impersonate, default latest version of Chrome. See details: `https://github.com/lwthiker/curl-impersonate/blob/main/browsers.json`.
            :proxy_url:str, constitute HTTP session proxies if present.
            :silent:bool, print realtime info on request if Not silent.
            :time_out:int, HTTP Request timeout, Default 30 seconds.

        """

        self._impersonate = impersonate
        self._proxies: dict[str, str] = {}

        self._proxy_url = proxy_url
        self._silent = silent
        self._timeout = timeout

        if not BrowserType.has(impersonate):
            msg = f"Browser Type Error: `{impersonate}`! \nAvailable:"
            msg += "\n".join(BrowserType.__members__)
            raise ValueError(msg)

        # Only HTTP|Socks5 Proxy Supported
        if proxy_url:
            if not (proxy_url.startswith("http") or proxy_url.startswith("socks")):
                raise ValueError("Proxy Scheme Error!")

            self._proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

    def header_set(
        self,
        key: str,
        value: Optional[str] = None,
    ) -> None:
        """Set session header value with key string, set None to delete."""
        key_name = ""
        for name in self._session.headers.keys():
            name_lower = name.lower()
            if name_lower == key.lower():
                key_name = name

        if key_name:
            if value is not None:
                self._session.headers[key_name] = value
            else:
                del self._session.headers[key_name]

        else:
            if value is not None:
                self._session.headers[key] = value

    def header_get(self, key: str) -> str:
        """Get session header value by key string."""
        for name in self._session.headers.keys():
            name_lower = name.lower()
            if name_lower == key.lower():
                return self._session.headers[name]
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


class HTTPBasic(HTTPBase):
    """HTTP Basic Client, for Fast Operation with Prototype.

    Features:
        - Custom Headers Operation
        - Cookies Operation

    """

    _session: Session

    def __init__(
        self,
        impersonate: str = "chrome",
        proxy_url: str = "",
        silent: bool = False,
        timeout: int = 30,
    ) -> None:
        """Init HTTP Basic Client.

        :Parameters:
            :impersonate:str, Browser Types to impersonate, default latest version of Chrome. See details: `https://github.com/lwthiker/curl-impersonate/blob/main/browsers.json`.
            :proxy_url:str, constitute HTTP session proxies if present.
            :silent:bool, print realtime info on request if Not silent.
            :time_out:int, HTTP Request timeout, Default 30 seconds.

        """
        super().__init__(
            impersonate=impersonate,
            proxy_url=proxy_url,
            silent=silent,
            timeout=timeout,
        )

        self._session = Session(
            impersonate=impersonate,
            proxy=proxy_url,
            # proxies=self._proxies,
            timeout=timeout,
        )

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

        except RequestsError as error:
            if debug:
                raise error

        return None

    def get(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP GET Method."""
        return self.req("GET", url, debug=debug, **kwargs)

    def post(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP POST Method."""
        return self.req("POST", url, debug=debug, **kwargs)

    def head(self, url: str, debug: bool = False, **kwargs: Any) -> Optional[Response]:
        """HTTP HEAD Method."""
        return self.req("HEAD", url, debug=debug, **kwargs)

    def options(
        self, url: str, debug: bool = False, **kwargs: Any
    ) -> Optional[Response]:
        """HTTP OPTIONS Method."""
        return self.req("OPTIONS", url, debug=debug, **kwargs)

    def connect(
        self, url: str, debug: bool = False, **kwargs: Any
    ) -> Optional[Response]:
        """HTTP CONNECT Method."""
        return self.req("CONNECT", url, debug=debug, **kwargs)

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


class AsyncHTTPBasic(HTTPBase):
    """Async HTTP Basic Client, for Fast Operation with Prototype.

    Features:
        - Custom Headers Operation
        - Cookies Operation
        - Flexible Request Parameters
        - Async Support

    """

    _session: AsyncSession

    def __init__(
        self,
        impersonate: str = "chrome",
        proxy_url: str = "",
        silent: bool = False,
        timeout: int = 30,
    ) -> None:
        """Init HTTP Basic Async Client.

        :Parameters:
            :impersonate:str, Browser Types to impersonate, default latest version of Chrome. See details: `https://github.com/lwthiker/curl-impersonate/blob/main/browsers.json`.
            :proxy_url:str, constitute HTTP session proxies if present.
            :silent:bool, print realtime info on request if Not silent.
            :time_out:int, HTTP Request timeout, Default 30 seconds.

        """
        super().__init__(
            impersonate=impersonate,
            proxy_url=proxy_url,
            silent=silent,
            timeout=timeout,
        )

        self._session = AsyncSession(
            impersonate=impersonate,
            # proxies=self._proxies,
            proxy=proxy_url,
            timeout=timeout,
        )

    async def req(
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
            response = await self._session.request(method=method, url=url, **kwargs)
            if not self._silent:
                now = arrow.now().format()
                code = response.status_code
                length = len(response.text)
                message = f"{now} - [{code}]<{length}>{response.url}"
                print(message)

            return response

        except RequestsError as error:
            if debug:
                raise error

        return None

    async def get(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP GET Method."""
        return await self.req("GET", url, debug=debug, **kwargs)

    async def head(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP HEAD Method."""
        return await self.req("HEAD", url, debug=debug, **kwargs)

    async def post(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP POST Method."""
        return await self.req("POST", url, debug=debug, **kwargs)

    async def delete(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP DELETE Method."""
        return await self.req("DELETE", url, debug=debug, **kwargs)

    async def put(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP PUT Method."""
        return await self.req("PUT", url, debug=debug, **kwargs)

    async def patch(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP PATCH Method."""
        return await self.req("PATCH", url, debug=debug, **kwargs)

    async def options(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP OPTIONS Method."""
        return await self.req("OPTIONS", url, debug=debug, **kwargs)

    async def connect(
        self,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """HTTP CONNECT Method."""
        return await self.req("CONNECT", url, debug=debug, **kwargs)

