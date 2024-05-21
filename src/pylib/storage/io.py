# -*- coding: utf-8 -*-

"""Input/Output Operation For File System."""

from pathlib import Path
from typing import List, Union

import orjson


__all__ = ("IO",)


class IO:
    """Input Output."""

    @classmethod
    def dir_create(cls, dir_name: Union[str, Path]) -> bool:
        """create directory"""
        path = Path(dir_name)
        path.mkdir(parents=True, exist_ok=True)
        return path.is_dir()

    @classmethod
    def dir_del(cls, dir_name: Union[str, Path], remain_root: bool = False) -> bool:
        """Delete directory with option to remain root."""
        path = Path(dir_name)
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
    def file_del(cls, file_name: Union[str, Path]) -> bool:
        """delete file if exsts"""
        path = Path(file_name)
        path.unlink(missing_ok=True)
        return path.is_file() is False

    @classmethod
    def load_str(cls, file_name: Union[str, Path], encoding: str = "utf8") -> str:
        """load string from file"""
        with open(file_name, "r", encoding=encoding) as file:
            return file.read()

    @classmethod
    def load_bytes(cls, file_name: Union[str, Path]) -> bytes:
        """load bytes from file"""
        with open(file_name, "rb") as file:
            return file.read()

    @classmethod
    def load_list(cls, file_name: Union[str, Path], encoding: str = "utf8") -> list:
        """load list from file"""
        with open(file_name, "r", encoding=encoding) as file:
            result = orjson.loads(file.read())
            if isinstance(result, list):
                return result
            raise ValueError(f"load_list error: {file_name}")

    @classmethod
    def load_dict(cls, file_name: Union[str, Path], encoding: str = "utf8") -> dict:
        """load dictionary from file"""
        with open(file_name, "r", encoding=encoding) as file:
            result = orjson.loads(file.read())
            if isinstance(result, dict):
                return result
            raise ValueError(f"load_dict error: {file_name}")

    @classmethod
    def load_list_list(
        cls, file_name: Union[str, Path], encoding: str = "utf8"
    ) -> List[list]:
        """load list of list from file"""
        with open(file_name, "r", encoding=encoding) as file:
            result = orjson.loads(file.read())
            if isinstance(result, list):
                if result and all(isinstance(_, list) for _ in result):
                    return result
            raise ValueError(f"load_list_list error: {file_name}")

    @classmethod
    def load_list_dict(
        cls, file_name: Union[str, Path], encoding: str = "utf8"
    ) -> List[dict]:
        """load list of dictionary from file"""
        with open(file_name, "r", encoding=encoding) as file:
            result = orjson.loads(file.read())
            if isinstance(result, list):
                if result and all(isinstance(_, dict) for _ in result):
                    return result
            raise ValueError(f"load_list_dict error: {file_name}")

    @classmethod
    def load_line(
        cls,
        file_name: Union[str, Path],
        encoding: str = "utf8",
        min_chars: int = 0,
        keyword: str = "",
    ) -> List[str]:
        """load lines of string from file"""
        result = []
        with open(file_name, "r", encoding=encoding) as file:
            result = [x.strip() for x in file.readlines()]
            if min_chars:
                result = [x for x in result if len(x) >= min_chars]
            if keyword:
                result = [x for x in result if keyword in x]
            return result

    @classmethod
    def save_str(
        cls, file_name: Union[str, Path], file_content: str, encoding: str = "utf8"
    ) -> None:
        """save string into file"""
        with open(file_name, "w", encoding=encoding) as file:
            file.write(file_content)

    @classmethod
    def save_bytes(cls, file_name: Union[str, Path], file_content: bytes) -> None:
        """save bytes into file"""
        with open(file_name, "wb") as file:
            file.write(file_content)

    @classmethod
    def save_dict(
        cls, file_name: Union[str, Path], file_data: dict, encoding: str = "utf8"
    ) -> None:
        """save dictionary into file"""
        with open(file_name, "w", encoding=encoding) as file:
            opt = orjson.OPT_INDENT_2
            file.write(orjson.dumps(file_data, option=opt).decode())

    @classmethod
    def save_list(
        cls, file_name: Union[str, Path], file_data: list, encoding: str = "utf8"
    ) -> None:
        """save list into file"""
        with open(file_name, "w", encoding=encoding) as file:
            opt = orjson.OPT_INDENT_2
            file.write(orjson.dumps(file_data, option=opt).decode())

    @classmethod
    def save_list_list(
        cls, file_name: Union[str, Path], file_data: List[list], encoding: str = "utf8"
    ) -> None:
        """save list of list into file"""
        with open(file_name, "w", encoding=encoding) as file:
            opt = orjson.OPT_INDENT_2
            file.write(orjson.dumps(file_data, option=opt).decode())

    @classmethod
    def save_list_dict(
        cls, file_name: Union[str, Path], file_data: List[dict], encoding: str = "utf8"
    ) -> None:
        """save list of dict into file"""
        with open(file_name, "w", encoding=encoding) as file:
            opt = orjson.OPT_INDENT_2
            file.write(orjson.dumps(file_data, option=opt).decode())

    @classmethod
    def save_line(
        cls,
        file_name: Union[str, Path],
        file_content: List[str],
        encoding: str = "utf8",
    ) -> None:
        """save lines of string into file"""
        with open(file_name, "w", encoding=encoding) as file:
            file.write("\n".join(file_content))

