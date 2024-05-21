from pathlib import Path

import loguru
import respx
from httpx import Response
from pylib.client.http2.advanced import (
    AsyncHTTPClient,
    HTTPClient,
    HTTPDebugger,
    HTTPDelayer,
)

from .test_abs import AbsTester


class TesterClient(AbsTester):
    """Test HTTPClient."""

    def test_logging(self, tmp_path: Path) -> None:
        """Test Logging."""
        file_log = tmp_path / "HTTPClient.log"
        logger = loguru.logger
        logger.add(sink=file_log)

        http = HTTPClient(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            logger=logger,
        )

        # GET Method
        response = http.get(url=self.url_get)
        assert response is not None
        assert response.status_code == 200

        assert file_log.is_file()

    def test_debugging(self, tmp_path: Path) -> None:
        """Test Debugging."""
        debugger_name = "HTTPClient"
        debugger = HTTPDebugger(
            name=debugger_name,
            dir=tmp_path,
        )
        http = HTTPClient(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            debugger=debugger,
        )

        # GET Method
        response = http.get(url=self.url_get, debug=True)
        assert response is not None
        assert response.status_code == 200

        # assert debugger file has content writed.
        assert bool(
            file.name.startswith(debugger_name) for file in tmp_path.glob("*.*")
        )

    @respx.mock
    def test_delaying(self) -> None:
        """Test Delaying."""
        http = HTTPClient(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            delayer=HTTPDelayer(),
        )

        # normal delaying
        assert http.delay(retry_after=2, debug=True) > 0

        # mock 429 errors and backoff delaying
        my_route = respx.get(self.url_mock).mock(
            return_value=Response(
                status_code=429,
            )
        )

        response = http.get(url=self.url_mock)
        assert my_route.called
        assert response is not None
        assert response.status_code == 429

        assert http.backoff_429(response=response, debug=True)
        assert http._delayer._errors.size()


class TesterAsyncHTTPClient(AbsTester):
    """Test AsyncHTTPClient."""

    async def test_logging(self, tmp_path: Path) -> None:
        """Test Logging."""
        file_log = tmp_path / "AsyncHTTPClient.log"
        logger = loguru.logger
        logger.add(sink=file_log)

        http = AsyncHTTPClient(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            logger=logger,
        )

        # GET Method
        response = await http.get(url=self.url_get)
        assert response is not None
        assert response.status_code == 200

        assert file_log.is_file()

        await http._session.aclose()

    async def test_debugging(self, tmp_path: Path) -> None:
        """Test Debugging."""
        debugger_name = "HTTPClient"
        debugger = HTTPDebugger(
            name=debugger_name,
            dir=tmp_path,
        )
        http = AsyncHTTPClient(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            debugger=debugger,
        )

        # GET Method
        response = await http.get(url=self.url_get, debug=True)
        assert response is not None
        assert response.status_code == 200

        # assert debugger file has content writed.
        assert bool(
            file.name.startswith(debugger_name) for file in tmp_path.glob("*.*")
        )

        await http._session.aclose()

    @respx.mock
    async def test_delaying(self) -> None:
        """Test Delaying."""
        http = AsyncHTTPClient(
            user_agent=self.user_agent,
            proxy_url=self.proxy_socks,
            delayer=HTTPDelayer(),
        )

        # normal delaying
        assert http.delay(retry_after=2, debug=True) > 0

        # mock 429 errors and backoff delaying
        my_route = respx.get(self.url_mock).mock(
            return_value=Response(
                status_code=429,
            )
        )

        response = await http.get(url=self.url_mock)
        assert my_route.called
        assert response is not None
        assert response.status_code == 429

        assert http.backoff_429(response=response, debug=True)
        assert http._delayer._errors.size()

        await http._session.aclose()
