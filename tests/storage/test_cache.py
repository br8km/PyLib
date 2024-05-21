
from pathlib import Path
from time import sleep, time
from threading import RLock, Thread

import pytest

from pylib.storage.cache import AbsCache, FileCache, MemoryCache, HybridCache
from pylib.storage.io import IO


@pytest.fixture()
def file_cache(tmp_path: Path) -> Path:
    """Temp File for Cache."""
    return tmp_path / "cache.json"



class Tester:
    """Test FileCache/MemoryCache/HybridCache."""

    seconds = 5
    lock = RLock()

    def test_abscache(self) -> None:
        """Test AbsCache."""
        app = AbsCache()

        assert app.now() <= int(time())

        item: dict[str, int] = {"name": "item_name", app.key_cache: app.now()}
        assert not app.is_expired(item=item, seconds=self.seconds)
        sleep(self.seconds + 1)
        assert app.is_expired(item=item, seconds=self.seconds)

    def test_filecache(self, file_cache: Path) -> None:
        """Test FileCache."""

        app = FileCache()

        # test filecache for any data
        assert not app.has_file(file=file_cache, seconds=self.seconds)

        # save file for string content
        IO.save_str(file_name=file_cache, file_content="hello")
        assert app.has_file(file=file_cache, seconds=self.seconds)

        # prune file
        app.prune_file(file=file_cache, seconds=self.seconds)
        # still exist
        assert app.has_file(file=file_cache, seconds=self.seconds)
        # wait for seconds + 1
        sleep(self.seconds + 1)
        # file been pruned
        assert not app.has_file(file=file_cache, seconds=self.seconds)

        # save file for bytes content
        IO.save_bytes(file_name=file_cache, file_content=b"hello")
        assert app.has_file(file=file_cache, seconds=self.seconds)
        sleep(self.seconds + 1)
        # wait for seconds + 1 and prune dir
        app.prune_dir(dir=file_cache.parent, seconds=self.seconds)
        # files from dir been pruned
        assert not app.has_file(file=file_cache, seconds=self.seconds)

        # cache operate for list of dict items
        items_ld: list[dict] = [{"age": age} for age in range(5)]

        # start with no cache
        result_ld = app.load_list_dict(file=file_cache, seconds=self.seconds)
        assert len(result_ld) == 0

        # add one item into cache
        app.add_list_dict(
            file=file_cache,
            item=items_ld[0],
            seconds=self.seconds,
        )
        result_ld = app.load_list_dict(file=file_cache, seconds=self.seconds)
        assert len(result_ld) == 1

        # add remain items into cache
        app.add_list_dict_many(
            file=file_cache,
            data=items_ld[1:],
            seconds=self.seconds,
        )
        # wait half of seconds defined before
        sleep(self.seconds / 2)
        result_ld = app.load_list_dict(file=file_cache, seconds=self.seconds)
        assert len(result_ld) == len(items_ld)

        # wait another half of seconds defined before plus 1
        sleep(self.seconds / 2 + 1)
        result_ld = app.load_list_dict(file=file_cache, seconds=self.seconds)
        assert len(result_ld) == 0

        # cache operate for dict of dict items
        items_dd: dict[str, dict] = {f"idx_{i}": {f"idx_{i}": i} for i in range(5)}

        # start with no cache
        file_cache.unlink(missing_ok=True)
        result_dd = app.load_dict_dict(file=file_cache, seconds=self.seconds)
        assert len(result_dd) == 0

        # add one key:value into cache
        key_0 = list(items_dd.keys())[0]
        value_0 = items_dd[key_0]
        app.add_dict_dict(
            file=file_cache,
            key=key_0,
            value=value_0,
            seconds=self.seconds,
        )
        result_dd = app.load_dict_dict(file=file_cache, seconds=self.seconds)
        assert len(result_dd) == 1

        # add remain items into cache
        remain = {k: v for k, v in items_dd.items() if k != key_0}
        app.add_dict_dict_many(
            file=file_cache,
            data=remain,
            seconds=self.seconds,
        )
        # wait half of seconds defined before
        sleep(self.seconds / 2)
        result_dd = app.load_dict_dict(file=file_cache, seconds=self.seconds)
        assert len(result_dd) == len(items_dd)

        # wait another half of seconds defined before plus 1
        sleep(self.seconds / 2 + 1)
        result_dd = app.load_dict_dict(file=file_cache, seconds=self.seconds)
        assert len(result_dd) == 0

        # clean up cache file
        file_cache.unlink(missing_ok=True)

    def test_memorycache(self) -> None:
        """Test MemoryCache."""

        # start with no cached item
        app = MemoryCache(seconds=self.seconds, lock=self.lock)
        assert app.size() == 0

        items_dd: dict[str, dict] = {f"idx_{i}": {f"idx_{i}": i} for i in range(5)}

        # add one key:value into cache
        key_0 = list(items_dd.keys())[0]
        value_0 = items_dd[key_0]
        app.add(
            key=key_0,
            value=value_0,
            force=False,
        )
        assert app.size() == 1

        # add remain items into cache
        remain = {k: v for k, v in items_dd.items() if k != key_0}
        app.add_many(
            items=remain,
            force=False,
        )
        # wait half of seconds defined before
        sleep(self.seconds / 2)
        assert app.size() == len(items_dd)

        # wait another half of seconds defined before plus 1
        sleep(self.seconds / 2 + 1)
        assert app.size() == 0

        # add all items again
        app.add_many(items=items_dd)
        assert app.size() == len(items_dd)

        # delete first key:value
        key_0 = list(items_dd.keys())[0]
        app.delete(key=key_0)
        assert app.size() == len(items_dd) - 1

        # delete another two key:value
        keys_2 = list(items_dd.keys())[1:3]
        app.delete_many(keys=keys_2)
        assert app.size() == len(items_dd) - 3

        # clear all items
        app.clear()
        assert app.size() == 0

    def test_hybridcache(self, file_cache: Path) -> None:
        """Test MemoryCache."""

        # start with no cached item
        app = HybridCache(file=file_cache, seconds=self.seconds, lock=self.lock)
        assert app.size() == 0

        items_dd: dict[str, dict] = {f"idx_{i}": {f"idx_{i}": i} for i in range(5)}

        # add one key:value into cache
        key_0 = list(items_dd.keys())[0]
        value_0 = items_dd[key_0]
        app.add(
            key=key_0,
            value=value_0,
            force=False,
        )
        assert app.size() == 1

        # add remain items into cache
        remain = {k: v for k, v in items_dd.items() if k != key_0}
        app.add_many(
            items=remain,
            force=False,
        )
        # wait half of seconds defined before
        sleep(self.seconds / 2)
        assert app.size() == len(items_dd)

        # wait another half of seconds defined before plus 1
        sleep(self.seconds / 2 + 1)
        assert app.size() == 0

        # add all items again
        app.add_many(items=items_dd)
        assert app.size() == len(items_dd)

        # delete first key:value
        key_0 = list(items_dd.keys())[0]
        app.delete(key=key_0)
        assert app.size() == len(items_dd) - 1

        # delete another two key:value
        keys_2 = list(items_dd.keys())[1:3]
        app.delete_many(keys=keys_2)
        assert app.size() == len(items_dd) - 3

        # save remain items into file
        assert app.save()

        # clear all items
        app.clear()
        assert app.size() == 0
        assert app.save()

    def test_memorycache_multi(self) -> None:
        """Test MemoryCache in multi-threading.

        Parameters:
            :num:int, number of threads, prefer 2 for basic, 20 for more.
            :seconds:int, number of seconds to cache.

        """
        numbers = [2, 20]
        for num in numbers:
            threads: list[Thread] = []
            for _ in range(num):
                th = Thread(
                    target=self.test_memorycache,
                    args=(),
                )
                threads.append(th)
                th.start()

            for th in threads:
                th.join()

            for th in threads:
                assert not th.is_alive()
