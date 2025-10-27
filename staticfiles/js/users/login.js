document.addEventListener('DOMContentLoaded', () => {

  const form = document.getElementById('loginForm');
  const email = document.getElementById('email');
  const pwd = document.getElementById('password');
  const toggle = document.getElementById('togglePwd');
  const emailHelp = document.getElementById('emailHelp');
  const pwdHelp = document.getElementById('pwdHelp');

  toggle.addEventListener('click', () => {
    if (pwd.type === 'password') {
      pwd.type = 'text';
      toggle.textContent = '숨기기';
    } else {
      pwd.type = 'password';
      toggle.textContent = '보기';
    }
  });

  function showError(el, msgEl, show) {
    if (show) {
      msgEl.classList.remove('hidden');
      el.setAttribute('aria-invalid', 'true');
    } else {
      msgEl.classList.add('hidden');
      el.removeAttribute('aria-invalid');
    }
  }

  form.addEventListener('submit', (e) => {
    let valid = true;

    if (!email.value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
      showError(email, emailHelp, true);
      valid = false;
    } else showError(email, emailHelp, false);

    if (!pwd.value || pwd.value.length < 6) {
      showError(pwd, pwdHelp, true);
      valid = false;
    } else showError(pwd, pwdHelp, false);

    if (!valid) {
      e.preventDefault();
    }
  });
});