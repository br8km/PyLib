"""HTTP Client."""

from dataclasses import asdict
from time import time
from typing import Any, Optional

import orjson
from httpx import Response
from httpx._exceptions import (
    DecodingError,
    NetworkError,
    ProtocolError,
    ProxyError,
    TimeoutException,
    TooManyRedirects,
)
from loguru._logger import Logger

from .basic import AsyncHTTPBasic, HTTPBasic
from .schema import DebugData, DebugRequest, DebugResponse, HTTPDebugger, HTTPDelayer


class HTTPMixin:
    """HTTP Clinet Mixin."""

    def _save_request(self, method: str, url: str, **kwargs: Any) -> None:
        """Save HTTP request information for debugger."""
        if self._debugger:
            params: dict[str, Any] = {}
            for key, value in kwargs.items():
                try:
                    orjson.dumps({"v": value})
                except TypeError:
                    value = str(value)
                params[key] = value

            cookies = dict(self._session.cookies.items())
            headers = dict(self._session.headers.items())

            # Get Request timestamp int/str
            time_stamp = int(time())

            self._debugger._data = DebugData(
                req=DebugRequest(
                    time_stamp=time_stamp,
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                ),
                res=DebugResponse(
                    time_stamp=time_stamp,
                    url="",
                    headers={},
                    cookies={},
                    success=False,
                    code=0,
                    text="",
                    json={},
                ),
            )

    def _save_response(self, response: Response) -> None:
        """Save HTTP response info for debugger."""
        if self._debugger:
            # Get Response timestamp int/str
            time_stamp = int(time())

            try:
                res_json = orjson.loads(response.text)
            except orjson.JSONDecodeError:
                res_json = {}

            cookies = dict(response.cookies.items())
            headers = dict(response.headers.items())

            self._debugger._data.res = DebugResponse(
                time_stamp=time_stamp,
                code=response.status_code,
                success=response.is_success,
                url=str(response.url),
                headers=headers,
                cookies=cookies,
                text=response.text,
                json=res_json,
            )

    # Custom Coding Part

    @staticmethod
    def _is_captcha(response: Response) -> bool:
        """Check if got Captcha page. Rewrite Logic to make it work."""
        raise NotImplementedError

    @staticmethod
    def _is_limited(response: Response) -> bool:
        """Check if got Rate-limited. Rewrite if Required."""
        return response.status_code == 429

    @staticmethod
    def _retry_after(response: Response) -> int:
        """Get delta-seconds to retry after requests.

        Notes:
            Based on Header Value of `RateLimit-Reset` or `Retry-After`.
            Check if Reasonabe before use it in production.

        """
        raise NotImplementedError

    def delay(self, retry_after: int = 2, debug: bool = False) -> float:
        """Smart Delaying. Rewrite if Required.

        Notes:
            You may select different delay method/parameters here, Eg:

            `self._delayer.near(1, 0.05)`
            `self._delayer.more_than(1, 0.05)`
            `self._delayer.less_than(1, 0.05)`

            OR use backoff delaying by using method `_backoff` below.

        """
        # Lazy Load Delayer
        if self._delayer is None:
            self._delayer = HTTPDelayer()

        return self._delayer.more_than(
            base=retry_after,
            percentage=0.05,
            debug=debug,
        )

    def backoff_429(
        self,
        response: Response,
        debug: bool = False,
    ) -> float:
        """Backoff Delaying.

        Note:
            Rewrite method `_is_limited` before use this method.
            Rewrite below code to suit your use case. You may want to select more appropriate backoff parameters.

        """
        # Lazy Load Delayer
        if self._delayer is None:
            self._delayer = HTTPDelayer()

        if response.status_code == 429:
            self._delayer._errors.add(
                key="limited", value={"code": 429},
            )

        return self._delayer.backoff(
            errors=self._delayer._errors.size(),
            debug=debug,
        )


class HTTPClient(HTTPBasic, HTTPMixin):
    """HTTP Client.

    Features:
        - HTTPBasic Features, and
        - Logging
        - Debugging
        - Backoff Delaying if Captcha/Limited

    """

    _logger: Optional[Logger]
    _debugger: Optional[HTTPDebugger]
    _delayer: Optional[HTTPDelayer]  # timestamp convert and backoff delaying

    def __init__(
        self,
        user_agent: str = "",
        proxy_url: str = "",
        http2: bool = True,
        silent: bool = False,
        timeout: int = 30,
        logger: Optional[Logger] = None,
        debugger: Optional[HTTPDebugger] = None,
        delayer: Optional[HTTPDelayer] = None,
    ) -> None:
        """Init HTTP Client.

        :Parameters:
            :user_agent:str, `User-Agent` Header;
            :proxy_url:str, proxies for session;
            :timeout:int, Deafult 30 seconds;
            :silent:bool, print realtime info on request if Not silent.
            :debugger: Optional `Debugger` if debugging;
            :logger:Logger from `loguru` library;

        """
        super().__init__(
            user_agent=user_agent,
            proxy_url=proxy_url,
            http2=http2,
            silent=silent,
            timeout=timeout,
        )

        self._debugger = debugger
        self._delayer = delayer
        self._logger = logger

    def req(
        self,
        method: str,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """Preform HTTP Request."""

        if debug and not self._debugger:
            raise TypeError("_debugger NOT exist!")

        if not kwargs.get("timeout", None):
            kwargs["timeout"] = self._timeout

        self._prepare_headers(**kwargs)

        if debug:
            self._save_request(method, url, **kwargs)

        try:
            response = self._session.request(method=method, url=url, **kwargs)
            if not self._silent:
                code = response.status_code
                length = len(response.text)
                message = f"[{code}]<{length}>{response.url}"
                if self._logger:
                    self._logger.info(message)
                else:
                    print(message)

            if debug:
                self._save_response(response)
                self._debugger.save(asdict(self._debugger._data))

            return response

        except (
            DecodingError,
            NetworkError,
            ProtocolError,
            ProxyError,
            TimeoutException,
            TooManyRedirects,
        ) as error:
            if self._logger:
                self._logger.exception(error)

            if debug and self._debugger:
                self._debugger.save(asdict(self._debugger._data))
                raise error

        return None

    def example_backoff(self, url: str, debug: bool, **kwargs) -> str:
        """EXAMPLE to get page html from url string with backoff delaying."""
        response = self.get(url=url, debug=debug, **kwargs)
        if response is not None:
            if self._delayer:
                if self._is_captcha(response=response):
                    self._delayer._errors.add(
                        key="captcha", value={"code": 500},
                    )
                if self._is_limited(response=response):
                    self._delayer._errors.add(
                        key="limited", value={"code": 429},
                    )

                retry_after = self._retry_after(response=response)
                if retry_after:
                    self.delay(retry_after=retry_after, debug=debug)
                else:
                    self.backoff(debug=debug)

            return response.text

        return ""


class AsyncHTTPClient(AsyncHTTPBasic, HTTPMixin):
    """Async HTTP Client.

    Features:
        - AsyncHTTPBasic Features, and
        - Logging
        - Debugging
        - Backoff Delaying if Captcha/Limited

    """

    _logger: Optional[Logger]
    _debugger: Optional[HTTPDebugger]
    _delayer: Optional[HTTPDelayer]  # timestamp convert and backoff delaying

    def __init__(
        self,
        user_agent: str = "",
        proxy_url: str = "",
        http2: bool = True,
        silent: bool = False,
        timeout: int = 30,
        logger: Optional[Logger] = None,
        debugger: Optional[HTTPDebugger] = None,
        delayer: Optional[HTTPDelayer] = None,
    ) -> None:
        """Init HTTP Client.

        :Parameters:
            :user_agent:str, `User-Agent` Header;
            :proxy_url:str, proxies for session;
            :timeout:int, Deafult 30 seconds;
            :silent:bool, print realtime info on request if Not silent.
            :debugger: Optional `Debugger` if debugging;
            :logger:Logger from `loguru` library;

        """
        super().__init__(
            user_agent=user_agent,
            proxy_url=proxy_url,
            http2=http2,
            silent=silent,
            timeout=timeout,
        )

        self._debugger = debugger
        self._delayer = delayer
        self._logger = logger

    async def req(
        self,
        method: str,
        url: str,
        debug: bool = False,
        **kwargs: Any,
    ) -> Optional[Response]:
        """Preform HTTP Request."""

        if debug and not self._debugger:
            raise TypeError("_debugger NOT exist!")

        if not kwargs.get("timeout", None):
            kwargs["timeout"] = self._timeout

        self._prepare_headers(**kwargs)

        if debug:
            self._save_request(method, url, **kwargs)

        try:
            response = await self._session.request(method=method, url=url, **kwargs)
            if not self._silent:
                code = response.status_code
                length = len(response.text)
                message = f"[{code}]<{length}>{response.url}"
                if self._logger:
                    self._logger.info(message)
                else:
                    print(message)

            if debug:
                self._save_response(response)
                self._debugger.save(asdict(self._debugger._data))

            return response

        except (
            DecodingError,
            NetworkError,
            ProtocolError,
            ProxyError,
            TimeoutException,
            TooManyRedirects,
        ) as error:
            if self._logger:
                self._logger.exception(error)

            if debug and self._debugger:
                self._debugger.save(asdict(self._data))
                raise error

        return None

    async def example_backoff(self, ) -> str:
        """EXAMPLE with backoff delaying, SEE sync method beyond."""
        raise NotImplementedError

