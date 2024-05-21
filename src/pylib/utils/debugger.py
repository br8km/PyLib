"""Debugger."""

import json
from pathlib import Path
from typing import Union


__all__ = ("Debugger",)


class Debugger:
    """Debugger to generate string identities"""

    __slots__ = (
        "_name",
        "_dir",
        "_seperator",
        "_length",
        "_index",
    )

    def __init__(
        self,
        name: str,
        dir: Path,
        length: int = 6,
        seperator: str = "-",
    ) -> None:
        """Init Debugger.

        Paramenters:
            :name:str, Name of this debugger;
            :dir:Path, File Path of this debugger;
            :length: int, Length of debug file name Suffix;
            :seperator: str, file name seperator, Default: `-`;

        """
        # Assure name not Empty
        assert name != ""

        # Assure file suffix length >= 3
        assert length >= 3

        self._name = name
        self._dir = dir

        self._seperator = seperator
        self._length = length

        self._index: int = 0

    def _gen_filepath(self, extension: str) -> Path:
        """Generate debug file path from _index number.
        Parameters:
            :extension:str, debug file Extension;
        Notes:
            :suffix format: `[string]-[number]`, example: abcd-0000, abcd-0001, abcd-0002
        """
        suffix = "{}".format(self._index).rjust(self._length, "0")
        return self._dir / f"{self._name}{self._seperator}{suffix}.{extension}"

    def _cleanup(self) -> bool:
        """Delete All debug files generated from This debugger."""
        for file in self._dir.glob("*.*"):
            if file.name.startswith(self._name + self._seperator):
                file.unlink(missing_ok=True)
        return True

    def save(self, data: Union[str, list, dict], encoding: str = "utf8") -> bool:
        """save data to file inside debug directory"""

        # add debug index integer automaticlly
        self._index += 1

        # debug file extension
        if isinstance(data, str):
            extension = "txt"
        elif isinstance(data, (list, dict)):
            extension = "json"
        else:
            raise TypeError

        file_debug = self._gen_filepath(extension=extension)

        with open(file_debug, "w", encoding=encoding) as file:
            if isinstance(data, (list, dict)):
                file.write(json.dumps(data, indent=2))
            else:
                file.write(data)

        return file_debug.is_file()

