from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch
from django.core.cache.backends.locmem import LocMemCache


class MockCacheHelper:
    def __init__(self, cache: LocMemCache) -> None:
        self.cache = cache
    
    def set(self, key: str, value: Any, timeout: int | None = None) -> None:
        self.cache.set(key, value, timeout=timeout)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.cache.get(key, default)
    
    def delete(self, key: str) -> None:
        self.cache.delete(key)


@pytest.fixture(autouse=True)
def patch_cache(monkeypatch: MonkeyPatch) -> None:
    shared_cache = LocMemCache("default", {})

    # Django 전역 cache 객체 교체
    monkeypatch.setattr("django.core.cache.cache", shared_cache)

    # CacheHelper 모킹
    mock_cache_helper = MockCacheHelper(shared_cache)
    monkeypatch.setattr("config.utils.cache_helper.CacheHelper.set", mock_cache_helper.set)
    monkeypatch.setattr("config.utils.cache_helper.CacheHelper.get", mock_cache_helper.get)
    monkeypatch.setattr("config.utils.cache_helper.CacheHelper.delete", mock_cache_helper.delete)
