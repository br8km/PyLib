from pathlib import Path

import loguru
import responses

from .test_abs import AbsTester
from pylib.client.http.advanced import HTTPClient, HTTPDebugger, HTTPDelayer


class TesterClient(AbsTester):
    """Test HTTP Client."""

    def test_logging(self, tmp_path: Path) -> None:
        """Test Logging."""
        logger = loguru.logger
        file_log = tmp_path / "HTTPClient.log"
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

        # debugger file ok
        assert bool(
            file.name.startswith(debugger_name)
            for file in tmp_path.glob("*.*")
        )

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
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                url=self.url_mock,
                status=429,
            )
            response = http.get(url=self.url_mock)
            assert response is not None
            assert response.status_code == 429

            # backoff delaying
            assert http.backoff_429(response=response, debug=True)
            assert http._delayer._errors.size()

