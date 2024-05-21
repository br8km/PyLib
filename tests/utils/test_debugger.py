
from pathlib import Path

from pylib.utils.debugger import Debugger


class Tester:
    """Tester for Debugger."""

    name = "test_debugger_name"

    def test_debugger(self, tmp_path: Path) -> None:
        """Test debugger methods."""
        debugger = Debugger(name=self.name, dir=tmp_path)
        assert debugger._name == self.name
        assert debugger._index == 0

        extension = "json"
        file_debug = debugger._gen_filepath(extension=extension)
        assert file_debug.name.startswith(self.name)
        assert "0" * debugger._length in file_debug.name
        assert file_debug.name.endswith(extension)

        assert debugger.save(data="value")
        assert debugger.save(data=["value"])
        assert debugger.save(data={"key": "value"})
        assert debugger.save(data={"key": ["value"]})

        assert debugger._cleanup()
