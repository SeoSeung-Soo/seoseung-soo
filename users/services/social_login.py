import json
import logging
import os
import time
import urllib.parse
from typing import Any, Dict, Optional, Tuple, Union, cast

import jwt
import requests
from django.conf import settings
from django.db import IntegrityError, transaction
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from users.models import SocialUser, User

logger = logging.getLogger(__name__)

class SocialLoginService:
    @staticmethod
    def get_or_create_user(
        provider: str,
        social_id: str,
        email: Optional[str],
        extra_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[User], Optional[Union[bool, str]]]:
        if not social_id:
            return None, "소셜 ID 누락"

        if not email:
            email = f"{provider}_{social_id}@{provider}.anonymous"

        username = email.split("@")[0]

        try:
            with transaction.atomic():
                existing = (
                    SocialUser.objects.select_related("user")
                    .filter(provider=provider, social_id=social_id)
                    .first()
                )
                if existing:
                    return existing.user, False

                user, _ = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "username": username,
                        "first_name": (extra_info or {}).get("first_name", ""),
                        "last_name": (extra_info or {}).get("last_name", ""),
                        "profile_image": (extra_info or {}).get("profile_image", ""),
                        "personal_info_consent": False,
                        "terms_of_use": False,
                        "sns_consent_to_receive": False,
                        "email_consent_to_receive": False,
                    },
                )

                SocialUser.objects.create(
                    user=user,
                    provider=provider,
                    social_id=social_id,
                    email=email,
                )

            return user, True

        except IntegrityError:
            return None, "이미 연결된 소셜 계정입니다."
        except Exception as e:
            return None, f"DB 오류: {e}"



class GoogleLoginService:

    @staticmethod
    def _generate_unique_username(email: str) -> str:
        base_username = email.split('@')[0]
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        return username

    @staticmethod
    def verify_google_token(credential: str) -> Optional[Dict[str, Any]]:
        try:
            request = google_requests.Request()  # type: ignore
            idinfo = cast(Dict[str, Any], id_token.verify_oauth2_token(  # type: ignore
                credential,
                request,
                settings.GOOGLE_OAUTH2_CLIENT_ID,
                clock_skew_in_seconds=30
            ))

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            return idinfo
        except ValueError as e:
            logger.error(f"Google token verification error: {e}")
            return None
        except Exception as e:
            logger.error(f"Google token verification error: {e}")
            return None

    @staticmethod
    def get_or_create_user(google_user_info: Dict[str, Any]) -> Tuple[Optional[User], Optional[str]]:
        google_id = str(google_user_info.get("sub") or google_user_info.get("id") or "")
        if not google_id:
            return None, "Google 사용자 ID(sub)가 누락되었습니다."

        email = google_user_info.get("email")
        name = google_user_info.get("name", "")
        picture = google_user_info.get("picture", "")
        extra = {"first_name": name, "profile_image": picture}

        user, created_or_error = SocialLoginService.get_or_create_user("google", google_id, email, extra)
        if not user:
            return None, str(created_or_error)
        return user, None

    @classmethod
    def authenticate_user(cls, credential: str) -> Tuple[Optional[User], Optional[str]]:
        try:
            google_user_info = cls.verify_google_token(credential)
        except Exception as e:
            logger.exception(f"[GoogleLogin] Token verification failed: {e}")
            return None, "Google 토큰 검증 중 오류가 발생했습니다."

        if not google_user_info:
            return None, "Google 토큰 검증에 실패했습니다."

        user, error = cls.get_or_create_user(google_user_info)
        if error:
            logger.warning(f"[GoogleLogin] User creation failed: {error}")
            return None, "사용자 생성/조회에 실패했습니다."

        return user, None


class KakaoLoginService:

    @staticmethod
    def _generate_unique_username(nickname: str) -> str:
        base_username = nickname
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username

    @staticmethod
    def get_kakao_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        try:
            # 카카오 사용자 정보 API 호출
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(
                'https://kapi.kakao.com/v2/user/me',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data
                else:
                    logger.error(f"Kakao API returned unexpected data type: {type(data)}")
                    return None
            else:
                logger.error(f"Kakao API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Kakao user info error: {e}")
            return None

    @staticmethod
    def get_or_create_user(kakao_user_info: Dict[str, Any]) -> Tuple[Optional[User], Optional[str]]:
        kakao_id = str(kakao_user_info.get("id"))
        email = kakao_user_info.get("kakao_account", {}).get("email")
        nickname = kakao_user_info.get("kakao_account", {}).get("profile", {}).get("nickname", "")
        profile_image = kakao_user_info.get("kakao_account", {}).get("profile", {}).get("profile_image_url", "")
        extra = {"first_name": nickname, "profile_image": profile_image}
        user, created_or_error = SocialLoginService.get_or_create_user("kakao", kakao_id, email, extra)
        if not user:
            return None, str(created_or_error)
        return user, None

    @classmethod
    def authenticate_user(cls, access_token: str) -> Tuple[Optional[User], Optional[str]]:
        try:
            kakao_user_info = cls.get_kakao_user_info(access_token)
            if not kakao_user_info:
                return None, "카카오 사용자 정보 조회에 실패했습니다."

            user, error = cls.get_or_create_user(kakao_user_info)
            if error:
                return None, error

            if not user:
                return None, "사용자 생성/조회에 실패했습니다."

            return user, None
        except Exception as e:
            return None, str(e)


class NaverLoginService:

    AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
    TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
    PROFILE_URL = "https://openapi.naver.com/v1/nid/me"

    @staticmethod
    def get_login_url(state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "redirect_uri": os.getenv("NAVER_REDIRECT_URI"),
            "state": state,
        }

        query = urllib.parse.urlencode(params)
        return f"{NaverLoginService.AUTH_URL}?{query}"

    @staticmethod
    def get_access_token(code: str, state: str) -> Optional[str]:
        params = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
            "code": code,
            "state": state,
        }
        res = requests.get(NaverLoginService.TOKEN_URL, params=params)
        if res.status_code != 200:
            return None

        try:
            data: Dict[str, Any] = res.json()
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        access_token = data.get("access_token")
        if not access_token:
            return None

        return cast(Optional[str], access_token)

    @staticmethod
    def get_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(NaverLoginService.PROFILE_URL, headers=headers)

        if res.status_code != 200:
            return None

        data: Dict[str, Any] = res.json()
        result_code = data.get("resultcode")
        if result_code != "00":
            logging.error(f"Naver API returned error code: {result_code}")
            return None

        response_data = data.get("response")
        return cast(Optional[Dict[str, Any]], response_data)

    @staticmethod
    def create_or_get_user(user_info: Dict[str, Any]) -> Tuple[Optional[User], Optional[str]]:
        """
        네이버 사용자 정보를 기반으로 SocialLoginService 호출
        """
        if not user_info:
            return None, "네이버 사용자 정보가 비어있습니다."

        naver_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name", "")

        if not naver_id:
            return None, "네이버 사용자 ID가 없습니다."
        if not email:
            return None, "네이버 이메일 정보가 없습니다."

        extra_info = {"first_name": name}

        user, created_or_error = SocialLoginService.get_or_create_user("naver", str(naver_id), email, extra_info)
        if not user:
            return None, str(created_or_error)
        return user, None


class AppleLoginService:
    AUTH_URL = "https://appleid.apple.com/auth/authorize"
    TOKEN_URL = "https://appleid.apple.com/auth/token"

    @staticmethod
    def _build_client_secret() -> str:
        """
        Apple OAuth client_secret(JWT) 생성
        """
        team_id = os.getenv("APPLE_TEAM_ID")
        client_id = os.getenv("APPLE_CLIENT_ID")
        key_id = os.getenv("APPLE_KEY_ID")
        private_key = os.getenv("APPLE_PRIVATE_KEY", "").replace("\\n", "\n")

        if not all([team_id, client_id, key_id, private_key]):
            raise ValueError("Apple OAuth 환경변수가 누락되었습니다.")

        iat = int(time.time())
        exp = iat + 60 * 10

        headers = {"kid": key_id, "alg": "ES256"}
        payload = {
            "iss": team_id,
            "iat": iat,
            "exp": exp,
            "aud": "https://appleid.apple.com",
            "sub": client_id,
        }

        token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
        return token if isinstance(token, str) else str(token)

    @staticmethod
    def get_login_url(state: str) -> str:
        """
        Apple 로그인 페이지로 리디렉션할 URL 생성
        """
        params = {
            "response_type": "code",
            "response_mode": "form_post",
            "client_id": os.getenv("APPLE_CLIENT_ID"),
            "redirect_uri": os.getenv("APPLE_REDIRECT_URI"),
            "scope": "name email",
            "state": state,
        }

        if not all([params["client_id"], params["redirect_uri"]]):
            raise ValueError("APPLE_CLIENT_ID / APPLE_REDIRECT_URI가 설정되지 않았습니다.")

        return f"{AppleLoginService.AUTH_URL}?{urllib.parse.urlencode(params)}"

    @staticmethod
    def exchange_token(code: str) -> Optional[Dict[str, Any]]:
        client_id = os.getenv("APPLE_CLIENT_ID")
        redirect_uri = os.getenv("APPLE_REDIRECT_URI")
        client_secret = AppleLoginService._build_client_secret()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }

        try:
            res = requests.post(AppleLoginService.TOKEN_URL, data=data, timeout=(5, 15))
        except Exception:
            return None

        if res.status_code != 200:
            return None

        try:
            token_payload = res.json()
        except ValueError:
            return None

        if not isinstance(token_payload, dict) or "error" in token_payload:
            return None

        return token_payload

    @staticmethod
    def parse_id_token(id_token: str) -> Optional[Dict[str, Any]]:
        """
        id_token(JWT)에서 사용자 정보 추출 및 검증
        """
        try:
            jwks_url = "https://appleid.apple.com/auth/keys"
            jwks_client = jwt.PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)

            decoded = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=os.getenv("APPLE_CLIENT_ID"),
                issuer="https://appleid.apple.com",
            )

            return cast(Dict[str, Any], decoded)
        except Exception as e:
            logger.exception(f"Failed to parse id_token: {e}")
            return None

    @staticmethod
    def authenticate_user(
            code: Optional[str] = None,
            id_token: Optional[str] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Apple 로그인 인증 처리:
        - id_token이 직접 주어지면 그대로 파싱
        - 아니면 code를 이용해 Apple 서버에서 id_token을 교환
        """
        id_info: Optional[Dict[str, Any]] = None

        if id_token is not None:
            id_info = AppleLoginService.parse_id_token(id_token)
            if not id_info:
                return None, "id_token 검증에 실패했습니다."

        else:
            if code is None:
                return None, "인가 코드(code)가 없습니다."

            token_payload = AppleLoginService.exchange_token(code)
            if not token_payload:
                return None, "애플 토큰 교환에 실패했습니다."

            id_token_raw = token_payload.get("id_token")
            if not isinstance(id_token_raw, str):
                return None, "id_token이 존재하지 않거나 문자열이 아닙니다."

            id_info = AppleLoginService.parse_id_token(id_token_raw)

        if not id_info:
            return None, "id_token 파싱 실패"

        sub = id_info.get("sub")
        email = id_info.get("email")
        if not sub or not email:
            return None, "애플 사용자 정보(sub/email) 확인에 실패했습니다."

        user_info = {"apple_id": sub, "email": email}
        user, error = AppleLoginService.create_or_get_user(user_info)
        if error:
            return None, error

        return user, None

    @staticmethod
    def create_or_get_user(user_info: Dict[str, Any]) -> Tuple[Optional[User], Optional[str]]:
        if not user_info:
            return None, "애플 사용자 정보가 비어있습니다."

        apple_id = user_info.get("apple_id")
        email = user_info.get("email")

        if not apple_id:
            return None, "애플 사용자 ID(sub)가 없습니다."

        user, created_or_error = SocialLoginService.get_or_create_user(
            provider="apple",
            social_id=str(apple_id),
            email=email or "",
        )
        if not user:
            return None, str(created_or_error)
        return user, None

