// 동의 페이지 전용 JavaScript
document.addEventListener('DOMContentLoaded', () => {
  console.log('동의 페이지 JavaScript 로드됨');
  
  // 동의 항목들
  const allConsent = document.getElementById('all_consent');
  const termsConsent = document.getElementById('terms_consent');
  const privacyConsent = document.getElementById('privacy_consent');
  const marketingConsent = document.getElementById('marketing_consent');
  const snsConsent = document.getElementById('sns_consent');
  const emailConsent = document.getElementById('email_consent');
  
  const form = document.querySelector('.signup-form');
  const consentBtn = document.querySelector('.signup-btn');

  console.log('요소들:', {
    allConsent: !!allConsent,
    termsConsent: !!termsConsent,
    privacyConsent: !!privacyConsent,
    marketingConsent: !!marketingConsent,
    snsConsent: !!snsConsent,
    emailConsent: !!emailConsent,
    form: !!form,
    consentBtn: !!consentBtn
  });

  // 전체 동의 체크박스 기능
  if (allConsent) {
    allConsent.addEventListener('change', () => {
      console.log('전체 동의 체크박스 변경:', allConsent.checked);
      const isChecked = allConsent.checked;
      if (termsConsent) {
        termsConsent.checked = isChecked;
        console.log('이용약관 체크:', termsConsent.checked);
      }
      if (privacyConsent) {
        privacyConsent.checked = isChecked;
        console.log('개인정보 체크:', privacyConsent.checked);
      }
      if (marketingConsent) {
        marketingConsent.checked = isChecked;
        console.log('쇼핑정보 체크:', marketingConsent.checked);
      }
      if (snsConsent) {
        snsConsent.checked = isChecked;
        console.log('SMS 체크:', snsConsent.checked);
      }
      if (emailConsent) {
        emailConsent.checked = isChecked;
        console.log('이메일 체크:', emailConsent.checked);
      }
      
      updateConsentButton();
    });
    
    // 클릭 이벤트도 추가
    allConsent.addEventListener('click', (e) => {
      console.log('전체 동의 클릭됨');
      setTimeout(() => {
        const isChecked = allConsent.checked;
        if (termsConsent) termsConsent.checked = isChecked;
        if (privacyConsent) privacyConsent.checked = isChecked;
        if (marketingConsent) marketingConsent.checked = isChecked;
        if (snsConsent) snsConsent.checked = isChecked;
        if (emailConsent) emailConsent.checked = isChecked;
        updateConsentButton();
      }, 10);
    });
  }

  // 개별 체크박스 변경 시 전체 동의 상태 업데이트
  function updateAllConsent() {
    if (!allConsent) return;
    
    const allChecked = (termsConsent && termsConsent.checked) && 
                      (privacyConsent && privacyConsent.checked) && 
                      (marketingConsent && marketingConsent.checked) && 
                      (snsConsent && snsConsent.checked) && 
                      (emailConsent && emailConsent.checked);
    allConsent.checked = allChecked;
    
    updateConsentButton();
  }

  // 동의 버튼 활성화/비활성화
  function updateConsentButton() {
    if (!consentBtn) return;
    
    const requiredChecked = (termsConsent && termsConsent.checked) && 
                           (privacyConsent && privacyConsent.checked);
    
    if (requiredChecked) {
      consentBtn.disabled = false;
      consentBtn.style.opacity = '1';
    } else {
      consentBtn.disabled = true;
      consentBtn.style.opacity = '0.6';
    }
  }

  // 개별 체크박스 이벤트 리스너
  if (termsConsent) {
    termsConsent.addEventListener('change', () => {
      console.log('이용약관 체크박스 변경:', termsConsent.checked);
      updateAllConsent();
      updateConsentButton();
    });
    termsConsent.addEventListener('click', () => {
      console.log('이용약관 클릭됨');
      setTimeout(() => {
        updateAllConsent();
        updateConsentButton();
      }, 10);
    });
  }
  
  if (privacyConsent) {
    privacyConsent.addEventListener('change', () => {
      console.log('개인정보 체크박스 변경:', privacyConsent.checked);
      updateAllConsent();
      updateConsentButton();
    });
    privacyConsent.addEventListener('click', () => {
      console.log('개인정보 클릭됨');
      setTimeout(() => {
        updateAllConsent();
        updateConsentButton();
      }, 10);
    });
  }

  // 쇼핑정보 수신 동의 체크 시 하위 항목들도 체크
  if (marketingConsent) {
    marketingConsent.addEventListener('change', () => {
      console.log('쇼핑정보 수신 동의 변경:', marketingConsent.checked);
      if (marketingConsent.checked) {
        if (snsConsent) snsConsent.checked = true;
        if (emailConsent) emailConsent.checked = true;
      } else {
        if (snsConsent) snsConsent.checked = false;
        if (emailConsent) emailConsent.checked = false;
      }
      updateAllConsent();
    });
    
    marketingConsent.addEventListener('click', () => {
      console.log('쇼핑정보 수신 동의 클릭됨');
      setTimeout(() => {
        if (marketingConsent.checked) {
          if (snsConsent) snsConsent.checked = true;
          if (emailConsent) emailConsent.checked = true;
        } else {
          if (snsConsent) snsConsent.checked = false;
          if (emailConsent) emailConsent.checked = false;
        }
        updateAllConsent();
      }, 10);
    });
  }

  // 하위 항목 체크 시 상위 항목도 체크
  if (snsConsent) {
    snsConsent.addEventListener('change', () => {
      console.log('SMS 수신 동의 변경:', snsConsent.checked);
      if (marketingConsent) {
        if (snsConsent.checked || (emailConsent && emailConsent.checked)) {
          marketingConsent.checked = true;
        } else {
          marketingConsent.checked = false;
        }
      }
      updateAllConsent();
    });
    
    snsConsent.addEventListener('click', () => {
      console.log('SMS 수신 동의 클릭됨');
      setTimeout(() => {
        if (marketingConsent) {
          if (snsConsent.checked || (emailConsent && emailConsent.checked)) {
            marketingConsent.checked = true;
          } else {
            marketingConsent.checked = false;
          }
        }
        updateAllConsent();
      }, 10);
    });
  }

  if (emailConsent) {
    emailConsent.addEventListener('change', () => {
      console.log('이메일 수신 동의 변경:', emailConsent.checked);
      if (marketingConsent) {
        if ((snsConsent && snsConsent.checked) || emailConsent.checked) {
          marketingConsent.checked = true;
        } else {
          marketingConsent.checked = false;
        }
      }
      updateAllConsent();
    });
    
    emailConsent.addEventListener('click', () => {
      console.log('이메일 수신 동의 클릭됨');
      setTimeout(() => {
        if (marketingConsent) {
          if ((snsConsent && snsConsent.checked) || emailConsent.checked) {
            marketingConsent.checked = true;
          } else {
            marketingConsent.checked = false;
          }
        }
        updateAllConsent();
      }, 10);
    });
  }

  // 초기 상태 설정
  updateConsentButton();
  
  // 디버깅을 위한 추가 로그
  console.log('초기 상태 설정 완료');
  console.log('현재 체크박스 상태:', {
    allConsent: allConsent ? allConsent.checked : 'N/A',
    termsConsent: termsConsent ? termsConsent.checked : 'N/A',
    privacyConsent: privacyConsent ? privacyConsent.checked : 'N/A',
    marketingConsent: marketingConsent ? marketingConsent.checked : 'N/A',
    snsConsent: snsConsent ? snsConsent.checked : 'N/A',
    emailConsent: emailConsent ? emailConsent.checked : 'N/A'
  });

  // 폼 제출 시 유효성 검사
  if (form) {
    form.addEventListener('submit', (e) => {
      // 필수 동의 항목 체크
      if (termsConsent && !termsConsent.checked) {
        e.preventDefault();
        alert('이용약관에 동의해주세요.');
        termsConsent.focus();
        return false;
      }

      if (privacyConsent && !privacyConsent.checked) {
        e.preventDefault();
        alert('개인정보 수집 및 이용에 동의해주세요.');
        privacyConsent.focus();
        return false;
      }
    });
  }
  
  // 체크박스 클릭 시 내용 펼치기/접기
  const consentCheckboxes = document.querySelectorAll('.consent-checkbox input[type="checkbox"]');
  
  consentCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      const content = this.closest('.consent-item').querySelector('.consent-content');
      if (content) {
        if (this.checked) {
          content.style.maxHeight = '400px';
        } else {
          content.style.maxHeight = '0';
        }
      }
    });
  });
});
