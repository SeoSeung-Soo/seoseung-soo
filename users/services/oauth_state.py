import uuid

from django.core.cache import cache


class OAuthStateService:
    """Apple OAuth state를 Redis TTL 기반으로 관리"""

    TTL_SECONDS = 600  # 10분 유효

    @staticmethod
    def create_state() -> str:
        """새로운 state 생성 및 Redis에 TTL 저장"""
        state = str(uuid.uuid4())
        cache.set(f"apple_oauth_state:{state}", True, timeout=OAuthStateService.TTL_SECONDS)
        return state

    @staticmethod
    def validate_state(state: str) -> bool:
        """Redis에서 state 검증 및 1회성 삭제"""
        key = f"apple_oauth_state:{state}"
        exists = cache.get(key)
        if exists:
            cache.delete(key)
            return True
        return False