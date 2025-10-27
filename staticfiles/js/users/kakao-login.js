function kakaoLogin() {
    const currentDomain = window.location.origin;
    
    if (!Kakao.isInitialized()) {
        Kakao.init(window.kakaoRestApiKey);
    }
    
    const kakaoClientId = window.kakaoRestApiKey;
    const kakaoLoginUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${kakaoClientId}&redirect_uri=${currentDomain}/users/auth/kakao/callback/&response_type=code&scope=profile_nickname,account_email`;
    
    window.location.href = kakaoLoginUrl;
}

function kakaoLogout() {
    Kakao.Auth.logout(function() {
    });
}

if (typeof Kakao !== 'undefined') {
    Kakao.init(window.kakaoRestApiKey);
    Kakao.isInitialized();
}
