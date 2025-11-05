import json
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from django.core.cache import cache as django_cache
from django_redis import get_redis_connection

if TYPE_CHECKING:
    from django_redis.client import DefaultClient


class CacheHelper:
    @staticmethod
    def _get_redis_client() -> "DefaultClient":
        return get_redis_connection("default")
    
    @staticmethod
    def _make_serializable(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: CacheHelper._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [CacheHelper._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    @staticmethod
    def _serialize(value: Any) -> str:
        serializable_value = CacheHelper._make_serializable(value)
        return json.dumps(serializable_value, ensure_ascii=False, indent=2)
    
    @staticmethod
    def _deserialize(value: str) -> Any:
        return json.loads(value)
    
    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> None:
        serialized_value = CacheHelper._serialize(value)
        redis_client = CacheHelper._get_redis_client()
        
        cache_key = django_cache.make_key(key)
        
        if timeout is not None:
            redis_client.setex(cache_key, timeout, serialized_value)
        else:
            redis_client.set(cache_key, serialized_value)
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        redis_client = CacheHelper._get_redis_client()
        cache_key = django_cache.make_key(key)
        
        value = redis_client.get(cache_key)
        
        if value is None:
            return default
        
        try:
            # bytes를 문자열로 변환
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            
            # JSON 파싱
            return CacheHelper._deserialize(value)
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
            # 기존 pickle 데이터가 있을 수 있으므로 Django 캐시로 폴백
            try:
                return django_cache.get(key, default)
            except Exception:
                return default
    
    @staticmethod
    def delete(key: str) -> None:
        redis_client = CacheHelper._get_redis_client()
        cache_key = django_cache.make_key(key)
        redis_client.delete(cache_key)

