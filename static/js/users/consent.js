document.addEventListener('DOMContentLoaded', () => {
  const allConsent = document.getElementById('all_consent');
  const termsConsent = document.getElementById('terms_consent');
  const privacyConsent = document.getElementById('privacy_consent');
  const marketingConsent = document.getElementById('marketing_consent');
  const snsConsent = document.getElementById('sns_consent');
  const emailConsent = document.getElementById('email_consent');
  
  const form = document.querySelector('.signup-form');
  const consentBtn = document.querySelector('.signup-btn');

  if (allConsent) {
    allConsent.addEventListener('change', () => {
      const isChecked = allConsent.checked;
      if (termsConsent) {
        termsConsent.checked = isChecked;
      }
      if (privacyConsent) {
        privacyConsent.checked = isChecked;
      }
      if (marketingConsent) {
        marketingConsent.checked = isChecked;
      }
      if (snsConsent) {
        snsConsent.checked = isChecked;
      }
      if (emailConsent) {
        emailConsent.checked = isChecked;
      }
      
      updateConsentButton();
    });
    
    allConsent.addEventListener('click', (e) => {
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

  if (termsConsent) {
    termsConsent.addEventListener('change', () => {
      updateAllConsent();
      updateConsentButton();
    });
    termsConsent.addEventListener('click', () => {
      setTimeout(() => {
        updateAllConsent();
        updateConsentButton();
      }, 10);
    });
  }
  
  if (privacyConsent) {
    privacyConsent.addEventListener('change', () => {
      updateAllConsent();
      updateConsentButton();
    });
    privacyConsent.addEventListener('click', () => {
      setTimeout(() => {
        updateAllConsent();
        updateConsentButton();
      }, 10);
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
    
    marketingConsent.addEventListener('click', () => {
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
    
    snsConsent.addEventListener('click', () => {
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

  updateConsentButton();

  if (form) {
    form.addEventListener('submit', (e) => {
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
