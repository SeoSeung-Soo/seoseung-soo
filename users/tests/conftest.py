import pytest
from _pytest.monkeypatch import MonkeyPatch
from django.core.cache.backends.locmem import LocMemCache


@pytest.fixture(autouse=True)
def patch_cache(monkeypatch: MonkeyPatch) -> None:
    shared_cache = LocMemCache("default", {})

    # Django 전역 cache 객체 교체
    monkeypatch.setattr("django.core.cache.cache", shared_cache)

    # OAuthStateService 모듈 내 캐시 객체 교체
    monkeypatch.setattr("users.services.oauth_state.cache", shared_cache)
