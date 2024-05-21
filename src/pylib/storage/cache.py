# -*- coding: utf-8 -*-

"""File Caches & Memory Caches.

Features:
- File Cache for General Caching Usage.
- Memory Cache for Fast Caching without File Storage Usage.
- Hybrid Cache for Fast caching with File Storage Usage.
- Bulk Operation
- Thread safe

TODO:
- sorting by value.keys?
- Iterable prefer?


"""

from pathlib import Path
from threading import RLock
from time import time
from typing import ItemsView, KeysView, Optional, ValuesView

from .io import IO

__all__ = (
    "FileCache",
    "MemoryCache",
    "HybridCache",
)


GLOBAL_LOCK = RLock()  # for threqd safe


class AbsCache:
    """Cache."""

    key_cache = "cache_time"

    @staticmethod
    def now() -> int:
        """Get utcnow timestamp."""
        return int(time())

    @classmethod
    def ts_expire(cls, seconds: int) -> int:
        """Get expected timestamp to be expired."""
        assert seconds >= 0
        return cls.now() - seconds

    @classmethod
    def is_expired(cls, item: dict, seconds: int) -> bool:
        """Check if item expired or not."""
        expired = cls.ts_expire(seconds=seconds)
        return item[cls.key_cache] <= expired


class FileCache(AbsCache):
    """File Cache in general usage.

    Notes:
        - To Avoid Frequent File Operation, Please Use Memory Cache.

    """

    # --- cache for Any data

    @classmethod
    def has_file(cls, file: Path, seconds: int) -> bool:
        """Has cached file for seconds or Not."""
        with GLOBAL_LOCK:
            expired = cls.ts_expire(seconds=seconds)
            return bool(file.is_file() and file.stat().st_mtime > expired)

    @classmethod
    def prune_file(cls, file: Path, seconds: int) -> None:
        """Prune cache file expired out of seconds."""
        with GLOBAL_LOCK:
            expired = cls.ts_expire(seconds=seconds)
            if file.is_file() and file.stat().st_mtime <= expired:
                file.unlink()

    @classmethod
    def prune_dir(cls, dir: Path, seconds: int) -> None:
        """Prune cache files from dir which expired out of seconds."""
        with GLOBAL_LOCK:
            expired = cls.ts_expire(seconds=seconds)
            for fp in dir.iterdir():
                if fp.is_file() and fp.stat().st_mtime <= expired:
                    fp.unlink()

    # --- cache for list of dict

    @classmethod
    def prune_list_dict(cls, data: list[dict], seconds: int) -> list[dict]:
        """Prune list of dict."""
        expired = cls.ts_expire(seconds=seconds)
        return [item for item in data if item[cls.key_cache] > expired]

    @classmethod
    def load_list_dict(cls, file: Path, seconds: int) -> list[dict]:
        """Load list of user dict from local cache."""
        with GLOBAL_LOCK:
            result: list[dict] = []
            if file.is_file():
                data = IO.load_list_dict(file)
                return cls.prune_list_dict(data=data, seconds=seconds)
            return result

    @classmethod
    def add_list_dict(cls, file: Path, item: dict, seconds: int) -> bool:
        """Add one item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_list_dict(file=file, seconds=seconds)
            item[cls.key_cache] = cls.now()
            cached.append(item)
            IO.save_list_dict(file_name=file, file_data=cached)
            return file.is_file()

    @classmethod
    def add_list_dict_many(cls, file: Path, data: list[dict], seconds: int) -> bool:
        """Save list of items into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_list_dict(file=file, seconds=seconds)
            for item in data:
                item[cls.key_cache] = cls.now()
                cached.append(item)
            IO.save_list_dict(file_name=file, file_data=cached)
            return file.is_file()

    # --- cache for dict of dict

    @classmethod
    def prune_dict_dict(cls, data: dict[str, dict], seconds: int) -> dict[str, dict]:
        """Prune dict of dict."""
        expired = cls.ts_expire(seconds=seconds)
        # result: dict[str, dict] = {}
        # for key: value in data.items():
        return {k: v for k, v in data.items() if v[cls.key_cache] > expired}

    @classmethod
    def load_dict_dict(cls, file: Path, seconds: int) -> dict[str, dict]:
        """Load dict of dict from local cache."""
        with GLOBAL_LOCK:
            result: dict[str, dict] = {}
            if file.is_file():
                data: dict[str, dict] = IO.load_dict(file)
                return cls.prune_dict_dict(data=data, seconds=seconds)
            return result

    @classmethod
    def add_dict_dict(cls, file: Path, key: str, value: dict, seconds: int) -> bool:
        """Add one key:item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_dict_dict(file=file, seconds=seconds)
            value[cls.key_cache] = cls.now()
            cached[key] = value
            IO.save_dict(file_name=file, file_data=cached)
            return file.is_file()

    @classmethod
    def add_dict_dict_many(
        cls, file: Path, data: dict[str, dict], seconds: int
    ) -> bool:
        """Add one key:item into local cache."""
        with GLOBAL_LOCK:
            cached = cls.load_dict_dict(file=file, seconds=seconds)
            for key, value in data.items():
                value[cls.key_cache] = cls.now()
                cached[key] = value
            IO.save_dict(file_name=file, file_data=cached)
            return file.is_file()


class MemoryCache(AbsCache):
    """Memory Cache."""

    _seconds: int
    _lock: RLock
    _cache: dict[str, dict]

    def __init__(self, seconds: int = 86400 * 7, lock: Optional[RLock] = None) -> None:
        """Init."""
        self._seconds = seconds
        self._lock = lock if lock else RLock()
        self._cache = {}

    def prune(self) -> int:
        """Prune any expired items from cache.

        Returns:
            number of pruned items which expired as of now.

        """
        with self._lock:
            return self._prune()

    def _prune(self) -> int:
        """_prune."""
        count = 0
        for key in self.keys():
            value = self._cache[key]
            if self.is_expired(item=value, seconds=self._seconds):
                count += self._delete(key)
        return count

    def set(self, key: str, value: dict) -> None:
        """Set key:value for cache."""
        with self._lock:
            return self._set(key=key, value=value)

    def _set(self, key: str, value: dict) -> None:
        """_Set key:value for cache."""
        value[self.key_cache] = self.now()
        self._cache[key] = value

    def set_many(self, items: dict[str, dict]) -> None:
        """Set many key:value for cache data."""
        with self._lock:
            self._set_many(items=items)

    def _set_many(self, items: dict[str, dict]) -> None:
        """_Set many key:value for cache."""
        for key, value in items.items():
            self._set(key=key, value=value)

    def add(self, key: str, value: dict, force: bool = False) -> None:
        """Add key:value into cache, set force to update if exist."""
        with self._lock:
            self._add(key=key, value=value, force=force)

    def _add(self, key: str, value: dict, force: bool = False) -> None:
        """_Add key:value into cache, set force to update if exist."""
        if self._has(key) and not force:
            return
        self._set(key=key, value=value)

    def add_many(self, items: dict[str, dict], force: bool = False) -> None:
        """Add many key:value into cache, set force to update if exist."""
        with self._lock:
            self._add_many(items=items, force=force)

    def _add_many(self, items: dict[str, dict], force: bool = False) -> None:
        """Add many key:value into cache, set force to update if exist."""
        for key, value in items.items():
            self._add(key=key, value=value, force=force)

    def delete(self, key: str) -> int:
        """Delete item."""
        with self._lock:
            return self._delete(key=key)

    def _delete(self, key: str) -> int:
        """Delete item for cache by key string."""
        count = 0
        try:
            del self._cache[key]
            count += 1
        except KeyError:
            pass
        return count

    def delete_many(self, keys: list[str]) -> int:
        """Delete many items."""
        with self._lock:
            return self._delete_many(keys=keys)

    def _delete_many(self, keys: list[str]) -> int:
        """Delete many items from cache by keys."""
        count = 0
        for key in keys:
            count += self._delete(key)
        return count

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def copy(self) -> dict[str, dict]:
        """Return a copy of the cache."""
        with self._lock:
            return self._cache.copy()

    def keys(self) -> KeysView:
        """
        Return ``dict_keys`` view of all cache keys.

        Note:
            Cache is copied from the underlying cache storage before returning.
        """
        return self._cache.copy().keys()

    def values(self) -> ValuesView:
        """
        Return ``dict_values`` view of all cache values.

        Note:
            Cache is copied from the underlying cache storage before returning.
        """
        return self._cache.copy().values()

    def items(self) -> ItemsView:
        """
        Return a ``dict_items`` view of cache items.

        Warning:
            Returned data is copied from the cache object, but any modifications to mutable values
            will modify this cache object's data.
        """
        return self._cache.copy().items()

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._clear()

    def _clear(self) -> None:
        """_clear."""
        self._cache.clear()

    def has(self, key: str) -> bool:
        """Return whether cache key exists and hasn't expired."""
        with self._lock:
            return self._has(key=key)

    def _has(self, key: str) -> bool:
        """Return whether cache key exists and hasn't expired."""
        value = self._get(key=key)
        return bool(value)

    def size(self, prune: bool = True) -> int:
        """Return number of cache entries."""
        with self._lock:
            if prune:
                self._prune()
            return len(self._cache)

    def get(self, key: str) -> dict:
        """Get cached item by key."""
        with self._lock:
            return self._get(key=key)

    def _get(self, key: str) -> dict:
        """Get cached item by key."""
        default: dict = {}
        try:
            value = self._cache.get(key, default)
            if value:
                if self.is_expired(item=value, seconds=self._seconds):
                    self._delete(key)
                    raise KeyError
        except KeyError:
            value = default
        return value


class HybridCache(MemoryCache):
    """Hybrid Cache, derived from MemoryCache add File Storage support."""

    _file: Path

    def __init__(
        self, file: Path, seconds: int = 86400 * 7, lock: Optional[RLock] = None
    ) -> None:
        """Init."""
        self._file = file
        self._seconds = seconds
        self._lock = lock if lock else RLock()
        self._cache = {}

        self.load()

    def load(self, prune: bool = True) -> bool:
        """Load cache data from File."""
        with self._lock:
            loaded = self._load()
            if prune:
                self._prune()
                return bool(self._cache)
            return loaded

    def _load(self) -> bool:
        """_load cache data from file."""
        if self._file.is_file():
            self._cache = IO.load_dict(self._file)
        return bool(self._cache)

    def save(self, prune: bool = True) -> bool:
        """Save cache data into File."""
        with self._lock:
            if prune:
                self._prune()
            return self._save()

    def _save(self) -> bool:
        """_save."""
        if self._cache:
            IO.save_dict(file_name=self._file, file_data=self._cache)
            return self._file.is_file()
        else:
            self._file.unlink(missing_ok=True)
            return not self._file.is_file()

