from pathlib import Path

import pytest
from pylib.client.http.downloader import HTTPDownloader

from .test_abs import AbsTester


class Tester(AbsTester):
    """Test HTTPDownloader Client.

    Warnings:
        - Not Finish Yet @ 20240521
            - Errors commonly Caused by Proxy!
            - Toooooo SLOW Caused by `GFW`

    """

    @pytest.mark.skip(reason="GFW")
    def test_download_direct(self, tmp_path: Path) -> None:
        """Test Download Direct File."""
        file_direct = tmp_path / "file_direct.jpg"
        http = HTTPDownloader(
            user_agent=self.user_agent,
            # proxy_url=self.proxy_socks,
            timeout=60,
        )
        assert http.download_direct(
            file_url=self.url_direct,
            file_out=file_direct,
        )

    @pytest.mark.skip(reason="GFW")
    def test_download_ranges(self, tmp_path: Path) -> None:
        """Test Download Ranges File."""
        file_ranges = tmp_path / "file_ranges.zip"
        http = HTTPDownloader(
            user_agent=self.user_agent,
            # proxy_url=self.proxy_socks,
            timeout=60,
        )
        assert http.download_ranges(
            file_url=self.url_ranges,
            file_out=file_ranges,
        )

    @pytest.mark.skip(reason="GFW")
    def test_download_zip(self, tmp_path: Path) -> None:
        """Test Download Zip Files."""
        dir_zip = tmp_path / "dir_zip"
        # new http client with longer timeout
        http = HTTPDownloader(
            user_agent=self.user_agent,
            # proxy_url=self.proxy_socks,
            timeout=3600,
        )
        buffer = http.download_bytes(file_url=self.url_zip)
        buffer_size = buffer.getbuffer().nbytes
        print(f"buffer_size = {buffer_size}")
        assert buffer_size
        assert http.unzip(buffer=buffer, dir_to=dir_zip)

    @pytest.mark.skip(reason="GFW")
    def test_download(self, tmp_path: Path) -> None:
        """Test Download File automatic select direct/range methods."""
        file_direct = tmp_path / "file_direct.jpg"
        file_ranges = tmp_path / "file_ranges.zip"

        http = HTTPDownloader(
            user_agent=self.user_agent,
            # proxy_url=self.proxy_socks,
            timeout=60,
        )

        assert http.download(
            file_url=self.url_direct,
            file_out=file_direct,
        )

        assert http.download(
            file_url=self.url_ranges,
            file_out=file_ranges,
        )
