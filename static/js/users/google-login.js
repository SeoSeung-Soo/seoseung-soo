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
  
  const responsePayload = decodeJWT(response.credential);
  
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

window.handleCredentialResponse = handleCredentialResponse;
