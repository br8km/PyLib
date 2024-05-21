"""HTTP Downloader Client."""

from io import BytesIO
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

from httpx import Response
from tqdm import tqdm

from ...storage.io import IO
from .basic import HTTPBasic

__all__ = ("HTTPDownloader",)


class HTTPDownloader(HTTPBasic):
    """HTTP Downloader Client for Resumable request to Large/Medium Files."""

    def __init__(
        self,
        user_agent: str = "",
        proxy_url: str = "",
        http2: bool = True,
        silent: bool = False,
        timeout: int = 30,
    ) -> None:
        """Init HTTP Downloader."""
        super().__init__(
            user_agent=user_agent,
            proxy_url=proxy_url,
            http2=http2,
            silent=silent,
            timeout=timeout,
        )

    def _head(self, file_url: str) -> Optional[Response]:
        """Head Request"""
        return self.head(file_url, timeout=self._timeout)

    @staticmethod
    def _has_range(response: Response) -> bool:
        """Check if accept range from response headers"""
        key_range = "Accept-Ranges".lower()
        return key_range in response.headers.keys()

    @staticmethod
    def _file_size(response: Response) -> int:
        """Parse file size from response headers"""
        return int(response.headers.get("content-length", 0))

    def download_direct(
        self,
        file_url: str,
        file_out: Path,
        chunk_size: int = 1024,
        debug: bool = False,
    ) -> bool:
        """Download In One Shot."""
        response = self.get(url=file_url, debug=debug)
        if response is None:
            raise ValueError("Response is None ERROR!")

        response.raise_for_status()
        total_size = self._file_size(response)
        with open(file_out, "wb") as file:
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
            for chunk in response.iter_bytes(chunk_size=chunk_size):
                file.write(chunk)
                file.flush()
                progress_bar.update(len(chunk))
                progress_bar.refresh()
            progress_bar.close()

        file_size = file_out.stat().st_size
        if debug:
            print(f"file_size = {file_size}")
            print(f"total_size = {total_size}")
        return file_size >= total_size

    def _resume_download(
        self,
        file_url: str,
        pos_start: int,
        pos_end: int = 0,
    ) -> Response:
        """
        Resume download
        Parameters:
            :pos_start:int, start position of range
            :pos_end:int, end position of range, empty if zero
        """
        _range = f"bytes={pos_start}-"
        if pos_end:
            _range = f"{_range}{pos_end}"
        self._session.headers["Range"] = _range

        return self.get(file_url)

    def download_ranges(
        self,
        file_url: str,
        file_out: Union[Path, str],
        chunk_size: int = 1024,
        block_size: int = 1024 * 1024,
        resume: bool = False,
        debug: bool = False,
    ) -> bool:
        """
        Downloading By Ranges.

        Steps:
            :check local file exists/size
            :get pos_start/pos_end
            :resume_download
            :append new chunk to file if present
        """

        # Cleanup downloaded file part.
        if not resume:
            IO.file_del(file_out)

        response = self._head(file_url=file_url)
        total_size = self._file_size(response=response)
        if not total_size:
            if debug:
                raise ValueError("File Size Error!")
            return False

        with open(file_out, "ab+") as file:
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

            index = 0
            while True:
                index += 1
                file_size = file_out.stat().st_size
                if file_size >= total_size:
                    break

                # fix error if pos_end > total_size [possible]?
                pos_end = min((file_size + block_size), total_size)

                if debug:
                    print()
                    print(f"<{index}>total_size = {total_size}")
                    print(f"<{index}>file_size = {file_size}")
                    print(f"<{index}>pos_end = {pos_end}")
                    print(
                        f"<{index}>header_range: {self._session.headers.get("range")}"
                    )

                response = self._resume_download(
                    file_url=file_url,
                    pos_start=file_size,
                    pos_end=pos_end,
                )
                if debug:
                    print(response, len(response.text))
                response.raise_for_status()
                for chunk in response.iter_bytes(chunk_size=chunk_size):
                    file.write(chunk)
                    file.flush()
                    progress_bar.update(len(chunk))
                    progress_bar.refresh()

                if pos_end >= total_size:
                    break

            progress_bar.close()

        file_size = file_out.stat().st_size
        if debug:
            print(f"file_size = {file_size}")
            print(f"total_size = {total_size}")
        return file_size >= total_size

    def download(
        self,
        file_url: str,
        file_out: Union[Path, str],
        debug: bool = False,
    ) -> bool:
        """Smart Download."""

        IO.dir_create(Path(file_out).parent)

        response = self._head(file_url)
        if response is None:
            raise ValueError("Response is None ERROR!")

        total_size = self._file_size(response)
        if not total_size:
            if debug:
                raise ValueError("File Size Error!")
            return False

        if self._has_range(response):
            return self.download_ranges(
                file_url=file_url,
                file_out=file_out,
                debug=debug,
            )

        return self.download_direct(
            file_url=file_url,
            file_out=file_out,
            debug=debug,
        )

    def download_bytes(
        self,
        file_url: str,
        chunk_size: int = 1024,
    ) -> BytesIO:
        """Download bytes data."""
        response = self.get(url=file_url)
        if response is None:
            raise ValueError("Response is None ERROR!")
        response.raise_for_status()

        total_size = self._file_size(response)
        # print(f"response.total_size = {total_size}")

        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
        buffer = BytesIO(response.content)
        for chunk in response.iter_bytes(chunk_size=chunk_size):
            buffer.write(chunk)
            progress_bar.update(len(chunk))
            progress_bar.refresh()
        progress_bar.close()

        return buffer

    @staticmethod
    def unzip(buffer: BytesIO, dir_to: Path) -> bool:
        """Unzip zipped bytes data into file path."""
        dir_to.mkdir(parents=True, exist_ok=True)

        with ZipFile(buffer) as file:
            file.extractall(str(dir_to.absolute()))
            return True

