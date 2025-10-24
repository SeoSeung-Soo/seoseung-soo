import json
import logging
import os
import time
import urllib.parse
from typing import Any, Dict, Optional, Tuple, cast

import jwt
import requests
from django.conf import settings
from django.db import transaction
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from users.models import User

logger = logging.getLogger(__name__)


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
    def get_or_create_user(google_user_info: Dict[str, Any]) -> User:
        try:
            google_id = google_user_info.get('sub')
            email = google_user_info.get('email')
            name = google_user_info.get('name', '')
            picture = google_user_info.get('picture', '')
            
            if not google_id or not email:
                raise ValueError("Google 사용자 정보가 없습니다.")
            
            with transaction.atomic():
                try:
                    user = User.objects.get(google_id=google_id)
                    return user
                except User.DoesNotExist:
                    pass
                
                # 2. 이메일로 기존 사용자 조회 및 Google ID 추가
                try:
                    user = User.objects.select_for_update().get(email=email)
                    user.google_id = google_id
                    user.save()
                    return user
                except User.DoesNotExist:
                    pass
                
                # 3. 새 사용자 생성
                username = GoogleLoginService._generate_unique_username(email)
                user = User.objects.create_user(
                    #TODO: 추후 배송수령인 데이터 이용
                    username=username,
                    email=email,
                    password=None,  # 소셜 로그인은 비밀번호 없음
                    google_id=google_id,
                    first_name=name.split(' ')[0] if name else '',
                    last_name=' '.join(name.split(' ')[1:]) if len(name.split(' ')) > 1 else '',
                    profile_image=picture,
                    is_active=True,
                    # 소셜 로그인 시 동의 항목은 false로 설정 (추후 동의 페이지에서 처리)
                    terms_of_use=False,
                    personal_info_consent=False,
                    sns_consent_to_receive=False,
                    email_consent_to_receive=False
                )
            
            return user
        except Exception as e:
            logger.error(f"User creation/retrieval error: {e}")
            raise ValueError(f"사용자 생성/조회 중 오류가 발생했습니다: {str(e)}")
    
    @classmethod
    def authenticate_user(cls, credential: str) -> Tuple[Optional[User], Optional[str]]:
        try:
            # 1. Google 토큰 검증
            google_user_info = cls.verify_google_token(credential)
            if not google_user_info:
                return None, "Google 토큰 검증에 실패했습니다."
            
            # 2. 사용자 생성 또는 조회
            user = cls.get_or_create_user(google_user_info)
            if not user:
                return None, "사용자 생성/조회에 실패했습니다."
            
            return user, None
        except Exception as e:
            return None, str(e)


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
    def get_or_create_user(kakao_user_info: Dict[str, Any]) -> User:
        try:
            kakao_id = str(kakao_user_info.get('id'))
            nickname = kakao_user_info.get('kakao_account', {}).get('profile', {}).get('nickname', '')
            email = kakao_user_info.get('kakao_account', {}).get('email', '')
            profile_image = kakao_user_info.get('kakao_account', {}).get('profile', {}).get('profile_image_url', '')
            
            if not kakao_id:
                raise ValueError("카카오 사용자 정보가 없습니다.")
            
            # 원자적 사용자 조회/생성 (경쟁 상태 방지)
            with transaction.atomic():
                # 1. 카카오 ID로 기존 사용자 조회
                try:
                    user = User.objects.get(kakao_id=kakao_id)
                    return user
                except User.DoesNotExist:
                    pass
                
                # 2. 이메일로 기존 사용자 조회 및 카카오 ID 추가
                if email:
                    try:
                        user = User.objects.select_for_update().get(email=email)
                        user.kakao_id = kakao_id
                        user.save()
                        return user
                    except User.DoesNotExist:
                        pass
                
                # 3. 새 사용자 생성 (닉네임을 username으로 사용)
                username = KakaoLoginService._generate_unique_username(nickname) if nickname else f"kakao_{kakao_id}"
                
                user = User.objects.create_user(
                    username=username,
                    email=email or f"kakao_{kakao_id}@kakao.com",  # 이메일이 없으면 임시 이메일 생성
                    password=None,  # 소셜 로그인은 비밀번호 없음
                    kakao_id=kakao_id,
                    first_name=nickname,
                    last_name='',
                    profile_image=profile_image,
                    is_active=True,
                    # 소셜 로그인 시 동의 항목은 false로 설정 (추후 동의 페이지에서 처리)
                    terms_of_use=False,
                    personal_info_consent=False,
                    sns_consent_to_receive=False,
                    email_consent_to_receive=False
                )
            
            return user
        except Exception as e:
            logger.error(f"User creation/retrieval error: {e}")
            raise ValueError(f"사용자 생성/조회 중 오류가 발생했습니다: {str(e)}")
    
    @classmethod
    def authenticate_user(cls, access_token: str) -> Tuple[Optional[User], Optional[str]]:
        try:
            # 1. 카카오 사용자 정보 조회
            kakao_user_info = cls.get_kakao_user_info(access_token)
            if not kakao_user_info:
                return None, "카카오 사용자 정보 조회에 실패했습니다."
            
            # 2. 사용자 생성 또는 조회
            user = cls.get_or_create_user(kakao_user_info)
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
        if not user_info:
            return None, "네이버 사용자 정보가 비어있습니다."

        naver_id = user_info.get("id")
        email = user_info.get("email", "")

        if not naver_id:
            return None, "네이버 사용자 ID가 없습니다."
        if not email:
            return None, "네이버 이메일 정보가 없습니다."

        username = GoogleLoginService._generate_unique_username(email)

        with transaction.atomic():
            user = User.objects.filter(naver_id=naver_id).first()
            if user:
                if user.email != email:
                    user.email = email
                    user.save(update_fields=["email"])
                return user, None

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "naver_id": naver_id,
                    "personal_info_consent": False,
                    "terms_of_use": False,
                },
            )

            if not created:
                user.naver_id = naver_id
                user.save(update_fields=["naver_id"])

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

        return cast(str, jwt.encode(payload, private_key, algorithm="ES256", headers=headers))

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
        id_token(JWT)에서 사용자 정보 추출
        """
        try:
            decoded = jwt.decode(
                id_token,
                options={"verify_signature": False, "verify_aud": False, "verify_iss": False},
                algorithms=["RS256", "ES256"],
            )
        except Exception:
            return None

        # 최소한의 무결성 체크(iss/aud)
        if decoded.get("iss") != "https://appleid.apple.com":
            return None
        if decoded.get("aud") != os.getenv("APPLE_CLIENT_ID"):
            return None

        return cast(Dict[str, Any], decoded)

    @staticmethod
    def authenticate_user(code: Optional[str] = None, id_token: Optional[str] = None) -> Tuple[
        Optional[User], Optional[str]]:
        """
        Apple 로그인 인증 처리:
        - id_token이 직접 주어지면 그대로 파싱
        - 아니면 code를 이용해 Apple 서버에서 id_token을 교환
        """
        # id_token이 직접 넘어온 경우
        if id_token:
            id_info = AppleLoginService.parse_id_token(id_token)
            if not id_info:
                return None, "id_token 검증에 실패했습니다."
        else:
            token_payload = AppleLoginService.exchange_token(code)
            if not token_payload:
                return None, "애플 토큰 교환에 실패했습니다."
            id_token = token_payload.get("id_token")
            id_info = AppleLoginService.parse_id_token(id_token)

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
        email = user_info.get("email") or f"{apple_id}@apple.anonymous"
        if not apple_id:
            return None, "애플 사용자 ID(sub)가 없습니다."

        username = GoogleLoginService._generate_unique_username(email)

        with transaction.atomic():
            user = User.objects.filter(apple_id=apple_id).first()
            if user:
                if email and user.email != email:
                    user.email = email
                    user.save(update_fields=["email"])
                return user, None

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "apple_id": apple_id,
                    "personal_info_consent": False,
                    "terms_of_use": False,
                },
            )

            if not created:
                user.apple_id = apple_id
                user.save(update_fields=["apple_id"])

        return user, None