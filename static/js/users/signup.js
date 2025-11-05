document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('signupForm');

  const username = document.getElementById('username');
  const email = document.getElementById('email');
  const pwd = document.getElementById('password');
  const pwdConfirm = document.getElementById('passwordConfirm');
  const phone_number = document.getElementById('phone_number');
  const phone1 = document.getElementById('phone1');
  const phone2 = document.getElementById('phone2');
  const phone3 = document.getElementById('phone3');
  const personal_info_consent = document.getElementById('personal_info_consent');
  const togglePwd = document.getElementById('togglePwd');
  const togglePwdConfirm = document.getElementById('togglePwdConfirm');

  const usernameHelp = document.getElementById('usernameHelp');
  const emailHelp = document.getElementById('emailHelp');
  const pwdHelp = document.getElementById('pwdHelp');
  const usernameDuplicateHelp = document.getElementById('usernameDuplicateHelp');
  const emailDuplicateHelp = document.getElementById('emailDuplicateHelp');

  let pwdConfirmHelp;
  if (pwdConfirm) {
    pwdConfirmHelp = document.createElement('p');
    pwdConfirmHelp.id = 'pwdConfirmHelp';
    pwdConfirmHelp.className = 'form-error hidden';
    pwdConfirmHelp.textContent = '비밀번호가 일치하지 않습니다.';
    pwdConfirm.parentNode.insertAdjacentElement('afterend', pwdConfirmHelp);
  }

  const allConsent = document.getElementById('all_consent');
  const termsConsent = document.getElementById('terms_consent');
  const privacyConsent = document.getElementById('privacy_consent');
  const marketingConsent = document.getElementById('marketing_consent');
  const snsConsent = document.getElementById('sns_consent');
  const emailConsent = document.getElementById('email_consent');

  function showError(el, msgEl, show) {
    if (show) {
      msgEl.classList.remove('hidden');
      el.setAttribute('aria-invalid', 'true');
    } else {
      msgEl.classList.add('hidden');
      el.removeAttribute('aria-invalid');
    }
  }

  togglePwd.addEventListener('click', () => {
    if (pwd.type === 'password') {
      pwd.type = 'text';
      togglePwd.textContent = '숨기기';
    } else {
      pwd.type = 'password';
      togglePwd.textContent = '보기';
    }
  });

  togglePwdConfirm.addEventListener('click', () => {
    if (pwdConfirm.type === 'password') {
      pwdConfirm.type = 'text';
      togglePwdConfirm.textContent = '숨기기';
    } else {
      pwdConfirm.type = 'password';
      togglePwdConfirm.textContent = '보기';
    }
  });

  function updatePhoneNumber() {
    if (!phone1 || !phone2 || !phone3 || !phone_number) return;
    
    const fullNumber = phone1.value + phone2.value + phone3.value;
    phone_number.value = fullNumber;
    
    if (phone1.value.length < 3) {
      phone1.classList.add('border-red-500');
    } else {
      phone1.classList.remove('border-red-500');
    }
    
    if (phone2.value.length < 4) {
      phone2.classList.add('border-red-500');
    } else {
      phone2.classList.remove('border-red-500');
    }
    
    if (phone3.value.length < 4) {
      phone3.classList.add('border-red-500');
    } else {
      phone3.classList.remove('border-red-500');
    }
    
    if (fullNumber.length === 11) {
      phone_number.setCustomValidity('');
    } else {
      phone_number.setCustomValidity('휴대폰 번호를 11자리 모두 입력해주세요.');
    }
  }

  function updateConsentStatus() {
    if (termsConsent) {
      const checkmark = termsConsent.nextElementSibling;
      if (checkmark && checkmark.classList.contains('checkmark')) {
        if (!termsConsent.checked) {
          checkmark.classList.add('border-red-500');
        } else {
          checkmark.classList.remove('border-red-500');
        }
      }
    }
    
    if (privacyConsent) {
      const checkmark = privacyConsent.nextElementSibling;
      if (checkmark && checkmark.classList.contains('checkmark')) {
        if (!privacyConsent.checked) {
          checkmark.classList.add('border-red-500');
        } else {
          checkmark.classList.remove('border-red-500');
        }
      }
    }
  }

  if (phone1) {
    phone1.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 3);
      if (e.target.value.length === 3 && phone2) {
        phone2.focus();
      }
      updatePhoneNumber();
    });
    
    phone1.addEventListener('keyup', (e) => {
      if (e.target.value.length === 3 && phone2) {
        setTimeout(() => {
          phone2.focus();
        }, 10);
      }
    });
  } else {
  }

  if (phone2) {
    phone2.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 4);
      if (e.target.value.length === 4 && phone3) {
        phone3.focus();
      }
      updatePhoneNumber();
    });
  }

  if (phone3) {
    phone3.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 4);
      updatePhoneNumber();
    });
  }

  if (phone1 && phone2 && phone3 && phone_number) {
    updatePhoneNumber();
  }

  if (pwdConfirm && pwdConfirmHelp) {
    pwdConfirm.addEventListener('input', () => {
      if (pwd && pwd.value === pwdConfirm.value) {
        showError(pwdConfirm, pwdConfirmHelp, false);
      }
    });
  }

  if (pwd && pwdConfirmHelp) {
    pwd.addEventListener('input', () => {
      if (pwdConfirm && pwd.value === pwdConfirm.value) {
        showError(pwdConfirm, pwdConfirmHelp, false);
      }
    });
  }

  let usernameTimeout;
  let emailTimeout;

  function checkDuplicate(type, value, duplicateHelpElement) {
    if (!value.trim()) return;
    
    const url = new URL('/users/check-duplicate/', window.location.origin);
    url.searchParams.set(type, value);
    
    fetch(url)
      .then(response => response.json())
      .then(data => {
        const result = data[type];
        if (result.available) {
          showError(document.getElementById(type), duplicateHelpElement, false);
        } else {
          duplicateHelpElement.textContent = result.message;
          showError(document.getElementById(type), duplicateHelpElement, true);
        }
      })
      .catch(error => {
      });
  }

  if (username) {
    username.addEventListener('input', () => {
      const value = username.value.trim();
      
      if (!value) {
        showError(username, usernameHelp, true);
        showError(username, usernameDuplicateHelp, false);
        return;
      }
      
      showError(username, usernameHelp, false);
      
      clearTimeout(usernameTimeout);
      usernameTimeout = setTimeout(() => {
        checkDuplicate('username', value, usernameDuplicateHelp);
      }, 500);
    });
  }

  if (email) {
    email.addEventListener('input', () => {
      const value = email.value.trim();
      
      if (!value) {
        showError(email, emailHelp, false);
        showError(email, emailDuplicateHelp, false);
        return;
      }
      
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        emailHelp.textContent = '올바른 이메일을 입력해주세요.';
        showError(email, emailHelp, true);
        showError(email, emailDuplicateHelp, false);
        return;
      }
      
      showError(email, emailHelp, false);
      
      clearTimeout(emailTimeout);
      emailTimeout = setTimeout(() => {
        checkDuplicate('email', value, emailDuplicateHelp);
      }, 500);
    });
  }

  if (allConsent) {
    allConsent.addEventListener('change', () => {
      const isChecked = allConsent.checked;
      if (termsConsent) termsConsent.checked = isChecked;
      if (privacyConsent) privacyConsent.checked = isChecked;
      if (marketingConsent) marketingConsent.checked = isChecked;
      if (snsConsent) snsConsent.checked = isChecked;
      if (emailConsent) emailConsent.checked = isChecked;
      updateConsentStatus();
    });
  }

  function updateAllConsent() {
    if (!allConsent) return;
    
    const allChecked = (termsConsent && termsConsent.checked) && 
                      (privacyConsent && privacyConsent.checked) && 
                      (marketingConsent && marketingConsent.checked) && 
                      (snsConsent && snsConsent.checked) && 
                      (emailConsent && emailConsent.checked);
    allConsent.checked = allChecked;
  }

  if (termsConsent) {
    termsConsent.addEventListener('change', () => {
      updateAllConsent();
      updateConsentStatus();
    });
  }
  
  if (privacyConsent) {
    privacyConsent.addEventListener('change', () => {
      updateAllConsent();
      updateConsentStatus();
    });
  }

  if (marketingConsent) {
    marketingConsent.addEventListener('change', () => {
      if (marketingConsent.checked) {
        if (snsConsent) snsConsent.checked = true;
        if (emailConsent) emailConsent.checked = true;
      } else {
        if (snsConsent) snsConsent.checked = false;
        if (emailConsent) emailConsent.checked = false;
      }
      updateAllConsent();
    });
  }

  if (snsConsent) {
    snsConsent.addEventListener('change', () => {
      if (marketingConsent) {
        if (snsConsent.checked || (emailConsent && emailConsent.checked)) {
          marketingConsent.checked = true;
        } else {
          marketingConsent.checked = false;
        }
      }
      updateAllConsent();
    });
  }

  if (emailConsent) {
    emailConsent.addEventListener('change', () => {
      if (marketingConsent) {
        if ((snsConsent && snsConsent.checked) || emailConsent.checked) {
          marketingConsent.checked = true;
        } else {
          marketingConsent.checked = false;
        }
      }
      updateAllConsent();
    });
  }

  if (form) {
    form.addEventListener('submit', (e) => {
      let valid = true;

      if (username && !username.value.trim()) {
        showError(username, usernameHelp, true);
        valid = false;
      } else if (username) {
        showError(username, usernameHelp, false);
      }

      if (email && (!email.value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value))) {
        showError(email, emailHelp, true);
        valid = false;
      } else if (email) {
        showError(email, emailHelp, false);
      }

      if (pwd && (!pwd.value || pwd.value.length < 6)) {
        showError(pwd, pwdHelp, true);
        valid = false;
      } else if (pwd) {
        showError(pwd, pwdHelp, false);
      }

      if (pwd && pwdConfirm && pwdConfirmHelp && pwd.value !== pwdConfirm.value) {
        showError(pwdConfirm, pwdConfirmHelp, true);
        valid = false;
      } else if (pwdConfirm && pwdConfirmHelp) {
        showError(pwdConfirm, pwdConfirmHelp, false);
      }

      if (phone1 && phone2 && phone3) {
        const fullPhoneNumber = phone1.value + phone2.value + phone3.value;
        if (fullPhoneNumber.length !== 11) {
          phone2.classList.add('border-red-500');
          phone3.classList.add('border-red-500');
          valid = false;
        } else {
          phone2.classList.remove('border-red-500');
          phone3.classList.remove('border-red-500');
        }
      }

      if (termsConsent && !termsConsent.checked) {
        const checkmark = termsConsent.nextElementSibling;
        if (checkmark && checkmark.classList.contains('checkmark')) {
          checkmark.classList.add('border-red-500');
        }
        termsConsent.focus();
        valid = false;
      }

      if (privacyConsent && !privacyConsent.checked) {
        const checkmark = privacyConsent.nextElementSibling;
        if (checkmark && checkmark.classList.contains('checkmark')) {
          checkmark.classList.add('border-red-500');
        }
        privacyConsent.focus();
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
        updateConsentStatus();
      }
    });
  }
  
  updatePhoneNumber();
  updateConsentStatus();
});
