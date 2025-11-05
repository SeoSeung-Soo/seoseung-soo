import uuid

from config.utils.cache_helper import CacheHelper


class OAuthStateService:
    TTL_SECONDS = 600

    @staticmethod
    def create_state() -> str:
        state = str(uuid.uuid4())
        CacheHelper.set(f"apple:oauth:state:{state}", True, timeout=OAuthStateService.TTL_SECONDS)
        return state

    @staticmethod
    def validate_state(state: str) -> bool:
        key = f"apple:oauth:state:{state}"
        exists = CacheHelper.get(key)
        if exists:
            CacheHelper.delete(key)
            return True
        return False