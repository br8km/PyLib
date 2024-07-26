# -*- coding: utf-8 -*-

"""Input/Output Operation For File System."""

from pathlib import Path
from typing import Generator, List, Union

import orjson

__all__ = ("IO",)


class IO:
    """Input Output."""

    @classmethod
    def dir_create(
        cls,
        folder: Union[str, Path],
    ) -> bool:
        """create directory"""
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        return path.is_dir()

    @classmethod
    def dir_del(
        cls,
        folder: Union[str, Path],
        remain_root: bool = False,
    ) -> bool:
        """Delete directory with option to remain root."""
        path = Path(folder)
        if not path.is_dir():
            return True

        for item in path.iterdir():
            if item.is_dir():
                cls.dir_del(item)
            else:
                item.unlink(missing_ok=True)
        if not remain_root:
            path.rmdir()
        return path.is_dir() == remain_root

    @classmethod
    def file_del(
        cls,
        file: Union[str, Path],
    ) -> bool:
        """delete file if exsts"""
        path = Path(file)
        path.unlink(missing_ok=True)
        return path.is_file() is False

    @classmethod
    def load_str(
        cls,
        file: Union[str, Path],
        encoding: str = "utf8",
    ) -> str:
        """load string from file"""
        with open(file, "r", encoding=encoding) as fp:
            return fp.read()

    @classmethod
    def load_bytes(
        cls,
        file: Union[str, Path],
    ) -> bytes:
        """load bytes from file"""
        with open(file, "rb") as fp:
            return fp.read()

    @classmethod
    def load_list(
        cls,
        file: Union[str, Path],
        encoding: str = "utf8",
    ) -> list:
        """load list from file"""
        with open(file, "r", encoding=encoding) as fp:
            result = orjson.loads(fp.read())
            if isinstance(result, list):
                return result
            raise ValueError(f"load_list error: {file}")

    @classmethod
    def load_dict(
        cls,
        file: Union[str, Path],
        encoding: str = "utf8",
    ) -> dict:
        """load dictionary from file"""
        with open(file, "r", encoding=encoding) as fp:
            result = orjson.loads(fp.read())
            if isinstance(result, dict):
                return result
            raise ValueError(f"load_dict error: {file}")

    @classmethod
    def load_list_list(
        cls,
        file: Union[str, Path],
        encoding: str = "utf8",
    ) -> List[list]:
        """load list of list from file"""
        with open(file, "r", encoding=encoding) as fp:
            result = orjson.loads(fp.read())
            if isinstance(result, list):
                if result and all(isinstance(_, list) for _ in result):
                    return result
            raise ValueError(f"load_list_list error: {file}")

    @classmethod
    def load_list_dict(
        cls,
        file: Union[str, Path],
        encoding: str = "utf8",
    ) -> List[dict]:
        """load list of dictionary from file"""
        with open(file, "r", encoding=encoding) as fp:
            result = orjson.loads(fp.read())
            if isinstance(result, list):
                if result and all(isinstance(_, dict) for _ in result):
                    return result
            raise ValueError(f"load_list_dict error: {file}")

    @classmethod
    def load_line(
        cls,
        file: Union[str, Path],
        encoding: str = "utf8",
        min_chars: int = 0,
        keyword: str = "",
    ) -> List[str]:
        """load lines of string from file"""
        result = []
        with open(file, "r", encoding=encoding) as fp:
            result = [x.strip() for x in fp.readlines()]
            if min_chars:
                result = [x for x in result if len(x) >= min_chars]
            if keyword:
                result = [x for x in result if keyword in x]
            return result

    @classmethod
    def save_str(
        cls,
        file: Union[str, Path],
        content: str,
        encoding: str = "utf8",
    ) -> bool:
        """save string into file"""
        with open(file, "w", encoding=encoding) as fp:
            fp.write(content)
        return file.exists()

    @classmethod
    def save_bytes(
        cls,
        file: Union[str, Path],
        content: bytes,
    ) -> bool:
        """save bytes into file"""
        with open(file, "wb") as fp:
            fp.write(content)
        return file.exists()

    @classmethod
    def save_dict(
        cls,
        file: Union[str, Path],
        item: dict,
        encoding: str = "utf8",
    ) -> bool:
        """save dictionary into file"""
        with open(file, "w", encoding=encoding) as fp:
            opt = orjson.OPT_INDENT_2
            fp.write(orjson.dumps(item, option=opt).decode())
        return file.exists()

    @classmethod
    def save_list(
        cls,
        file: Union[str, Path],
        items: list,
        encoding: str = "utf8",
    ) -> bool:
        """save list into file"""
        with open(file, "w", encoding=encoding) as fp:
            opt = orjson.OPT_INDENT_2
            fp.write(orjson.dumps(items, option=opt).decode())
        return file.exists()

    @classmethod
    def save_list_list(
        cls,
        file: Union[str, Path],
        items: List[list],
        encoding: str = "utf8",
    ) -> bool:
        """save list of list into file"""
        with open(file, "w", encoding=encoding) as fp:
            opt = orjson.OPT_INDENT_2
            fp.write(orjson.dumps(items, option=opt).decode())
        return file.exists()

    @classmethod
    def save_list_dict(
        cls,
        file: Union[str, Path],
        items: List[dict],
        encoding: str = "utf8",
    ) -> bool:
        """save list of dict into file"""
        with open(file, "w", encoding=encoding) as fp:
            opt = orjson.OPT_INDENT_2
            fp.write(orjson.dumps(items, option=opt).decode())
        return file.exists()

    @classmethod
    def save_line(
        cls,
        file: Union[str, Path],
        texts: List[str],
        encoding: str = "utf8",
    ) -> bool:
        """save lines of string into file"""
        with open(file, "w", encoding=encoding) as fp:
            fp.write("\n".join(texts))
        return file.exists()

    @classmethod
    def load_jsonl(
        cls,
        file: Path,
    ) -> Generator[dict, None, None]:
        """Load data from jsonl file."""
        with open(file, "r", encoding="utf-8") as fp:
            for line in fp:
                yield orjson.loads(line.strip())

    @classmethod
    def save_jsonl(
        cls,
        file: Path,
        data: Generator[dict, None, None],
    ) -> bool:
        """Save data into jsonl file."""
        with open(file, "w", encoding="utf-8") as fp:
            for item in data:
                fp.write(orjson.dumps(item).decode() + "\n")
        return file.is_file()
