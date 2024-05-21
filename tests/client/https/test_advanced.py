from pathlib import Path

import loguru

from pylib.client.https.advanced import (
    AsyncHTTPClient,
    HTTPClient,
    HTTPDebugger,
    HTTPDelayer,
)

from .test_abs import AbsTester


class TesterClient(AbsTester):
    """Test HTTP Client."""

    def test_logging(self, tmp_path: Path) -> None:
        """Test Logging."""
        file_log = tmp_path / "HTTPClient.log"
        logger = loguru.logger
        logger.add(sink=file_log)

        http = HTTPClient(
            logger=logger,
        )

        # GET Method
        response = http.get(url=self.url_get)
        assert response is not None
        assert response.status_code == 200

        # assert logger file
        assert file_log.is_file()

    def test_debugging(self, tmp_path: Path) -> None:
        """Test Debugging."""
        debugger_name = "HTTPClient"
        debugger = HTTPDebugger(
            name=debugger_name,
            dir=tmp_path,
        )
        http = HTTPClient(
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

    def test_delaying(self) -> None:
        """Test Delaying.

        Issues:
            - CANNOT Mock 429 error for curl_cffi libaray

        """
        http = HTTPClient(
            proxy_url=self.proxy_socks,
            delayer=HTTPDelayer(),
        )

        # normal delaying
        assert http.delay(retry_after=2, debug=True) > 0

        # CANNOT Mock 429 errors and backoff delaying
        # url = "https://httpbin.org/get"
        # with responses.RequestsMock() as rsps:
        #     rsps.add(
        #         responses.GET,
        #         url=url,
        #         status=429,
        #     )
        #     response = http.get(url=url, debug=True)
        #     assert response is not None
        #     assert response.status_code == 429

        # assert http.backoff(response=response, debug=True)
        # assert http._delayer._errors.size()


class TesterAsyncHTTPClient(AbsTester):
    """Tester for Async HTTP Client."""

    async def test_logging(self, tmp_path: Path) -> None:
        """Test Logging."""
        file_log = tmp_path / "AsyncHTTPClient.log"
        logger = loguru.logger
        logger.add(sink=file_log)

        http = AsyncHTTPClient(
            proxy_url=self.proxy_socks,
            logger=logger,
        )

        # GET Method
        response = await http.get(url=self.url_get)
        assert response is not None
        assert response.status_code == 200

        # assert logger file
        assert file_log.is_file()

        # close session
        await http._session.close()

    async def test_debugging(self, tmp_path: Path) -> None:
        """Test Debugging."""
        debugger_name = "AsyncHTTPClient"
        debugger = HTTPDebugger(
            name=debugger_name,
            dir=tmp_path,
        )
        http = AsyncHTTPClient(
            proxy_url=self.proxy_socks,
            debugger=debugger,
        )

        # GET Method
        response = await http.get(url=self.url_get, debug=True)
        assert response is not None
        assert response.status_code == 200

        # assert debugger file has content writed.
        assert bool(
            file.name.startswith(debugger_name)
            for file in tmp_path.glob("*.*")
        )

        # close session
        await http._session.close()

    async def test_delaying(self) -> None:
        """Test Delaying.

        Issues:
            - CANNOT Mock 429 error for curl_cffi libaray

        """
        http = AsyncHTTPClient(
            proxy_url=self.proxy_socks,
            delayer=HTTPDelayer(),
        )
        assert http._delayer

        # normal delaying
        assert http.delay(retry_after=2, debug=True) > 0

        # Mock 429 errors and backoff delaying
        # url = "https://httpbin.org/get"
        # with responses.RequestsMock() as rsps:
        #     rsps.add(
        #         responses.GET,
        #         url=url,
        #         status=429,
        #     )
        #     response = await http.get(url=url, debug=True)
        #     assert response is not None
        #     assert response.status_code == 429

        # assert http.backoff(response=response, debug=True)
        # assert http._delayer._errors.size()

        await http._session.close()
