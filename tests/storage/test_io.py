import random
from pathlib import Path

import pytest
from pylib.storage.io import IO


@pytest.fixture()
def temp_file(tmp_path: Path) -> Path:
    """Temp File."""
    return tmp_path / "test.file"


class Tester:
    """Test IO Operation."""

    io = IO()

    def test_dirs(self, tmp_path: Path) -> None:
        """Test directory operation."""
        folder = tmp_path / "test"
        folder_str = str(folder)

        assert self.io.dir_create(dir_name=folder)
        assert self.io.dir_del(dir_name=folder, remain_root=True)
        assert self.io.dir_del(dir_name=folder)

        assert self.io.dir_create(dir_name=folder_str)
        assert self.io.dir_del(dir_name=folder_str, remain_root=True)
        assert self.io.dir_del(dir_name=folder_str)

    def test_save_load_str(self, temp_file: Path) -> None:
        """test save_str, load_str"""
        content = "content"
        self.io.save_str(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_str(temp_file) == content
        assert self.io.file_del(temp_file)

    def test_save_load_bytes(self, temp_file: Path) -> None:
        """test save_bytes, load_bytes"""
        content = b"content"
        self.io.save_bytes(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_bytes(temp_file) == content
        assert self.io.file_del(temp_file)

    def test_save_load_line(self, temp_file: Path) -> None:
        """test save_line, load_line"""
        content = ["content"]
        self.io.save_line(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_line(temp_file) == content
        assert self.io.file_del(temp_file)

    def test_save_load_list(self, temp_file: Path) -> None:
        """test save_list, load_list"""
        content = [random.randint(0, 999) for _ in range(100)]
        self.io.save_list(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_list(temp_file) == content
        assert self.io.file_del(temp_file)

        content = []
        self.io.save_list(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_list(temp_file) == content
        assert self.io.file_del(temp_file)

    def test_save_load_dict(self, temp_file: Path) -> None:
        """test save_dict, load_dict"""
        content = {"name": "Ben", "age": 24, "float": 123.456}
        self.io.save_dict(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_dict(temp_file) == content
        assert self.io.file_del(temp_file)

        content = {"dict": content}
        self.io.save_dict(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_dict(temp_file) == content
        assert self.io.file_del(temp_file)

    def test_save_load_list_list(self, temp_file: Path) -> None:
        """test save_list_list, load_list_list"""
        content = [[random.randint(0, 999) for _ in range(100)] for _ in range(10)]
        self.io.save_list_list(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_list_list(temp_file) == content
        assert self.io.file_del(temp_file)

        content = [[]]
        self.io.save_list_list(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_list_list(temp_file) == content
        assert self.io.file_del(temp_file)

    def test_save_load_list_dict(self, temp_file: Path) -> None:
        """test save_list_dict, load_list_dict"""
        content = [{"name": "Ben", "age": 24, "float": 123.456} for _ in range(10)]
        self.io.save_list_dict(temp_file, content)
        assert temp_file.is_file()
        assert self.io.load_list_dict(temp_file) == content
        assert self.io.file_del(temp_file)
