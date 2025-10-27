// Google 로그인 전용 JavaScript (Django와 완전 분리)

function decodeJWT(token) {
  let base64Url = token.split(".")[1];
  let base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  let jsonPayload = decodeURIComponent(
    atob(base64)
      .split("")
      .map(function (c) {
        return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
      })
      .join("")
  );
  return JSON.parse(jsonPayload);
}

function handleCredentialResponse(response) {
  
  // JWT 디코딩
  const responsePayload = decodeJWT(response.credential);
  
  // Django 서버로 전송
  fetch('/users/auth/google/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({
      credential: response.credential,
      user_info: responsePayload
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      window.location.href = data.redirect_url || '/';
    } else {
      alert('로그인 실패: ' + data.message);
    }
  })
  .catch(error => {
    alert('로그인 중 오류가 발생했습니다.');
  });
}

// Google이 자동으로 초기화하도록 함 (콜백 함수만 전역에 등록)
window.handleCredentialResponse = handleCredentialResponse;
