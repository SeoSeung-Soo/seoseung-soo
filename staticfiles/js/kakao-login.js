// 카카오 로그인 함수
function kakaoLogin() {
    const currentDomain = window.location.origin;
    if (!Kakao.isInitialized()) {
        Kakao.init('{{ kakao_rest_api_key }}');
    }
    const kakaoClientId = '{{ kakao_rest_api_key }}';
    const kakaoLoginUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${kakaoClientId}&redirect_uri=${currentDomain}/users/auth/kakao/callback/&response_type=code&scope=profile_nickname,account_email`;
    window.location.href = kakaoLoginUrl;
}

function kakaoLogout() {
    Kakao.Auth.logout(function() {
        console.log('카카오 로그아웃 완료');
    });
}
