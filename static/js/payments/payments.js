document.addEventListener('DOMContentLoaded', function() {
    initializePaymentPage();
});

function initializePaymentPage() {
    setupPaymentMethodSelection();
    setupCouponApplication();
    setupAddressSearch();
    setupFormValidation();
    setupDiscountSelection();
    setupDropdownCloseOnOutsideClick();
    setupTossPayment();
}

function setupPaymentMethodSelection() {
    const paymentMethods = document.querySelectorAll('.payment-method');
    
    paymentMethods.forEach(method => {
        method.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const radio = this.querySelector('input[type="radio"]');
            const dropdownContainer = document.querySelector('.card-dropdown-container');
            
            if (radio.value === 'card' && this.classList.contains('selected')) {
                if (dropdownContainer) {
                    const isShowing = dropdownContainer.classList.contains('show');
                    setTimeout(() => {
                        dropdownContainer.classList.toggle('show');
                    }, 10);
                }
                return;
            }
            
            paymentMethods.forEach(m => {
                m.classList.remove('selected');
            });
            
            if (dropdownContainer) {
                dropdownContainer.classList.remove('show');
            }
            
            this.classList.add('selected');
            radio.checked = true;
            
            if (radio.value === 'card' && dropdownContainer) {
                setTimeout(() => {
                    dropdownContainer.classList.add('show');
                }, 50);
            }
            
        });
    });
    
    setupCardOptionSelection();
}

function setupCardOptionSelection() {
    const cardOptions = document.querySelectorAll('.card-option');
    
    cardOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const cardType = this.getAttribute('data-value');
            const cardName = this.querySelector('span').textContent;
            
            window.selectedCardType = cardType;
            
            const dropdown = this.closest('.card-dropdown');
            dropdown.classList.remove('show');
            
            updateSelectedCardDisplay(cardName);
        });
    });
}

function setupDropdownCloseOnOutsideClick() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.payment-method') || e.target.closest('.card-dropdown-container')) {
            return;
        }
        
        const dropdownContainer = document.querySelector('.card-dropdown-container.show');
        
        if (dropdownContainer) {
            dropdownContainer.classList.remove('show');
        }
    });
}

function setupCouponApplication() {
    const couponBtn = document.querySelector('.coupon-btn');
    const couponInput = document.querySelector('.coupon-input');
    
    if (couponBtn && couponInput) {
        couponBtn.addEventListener('click', function() {
            const couponCode = couponInput.value.trim();
            
            if (!couponCode) {
                alert('쿠폰 코드를 입력해주세요.');
                return;
            }
            
            applyCoupon(couponCode);
        });
        
        couponInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                couponBtn.click();
            }
        });
    }
}

function applyCoupon(couponCode) {
    const couponBtn = document.querySelector('.coupon-btn');
    const originalText = couponBtn.textContent;
    couponBtn.textContent = '적용 중...';
    couponBtn.disabled = true;
    
    setTimeout(() => {
        const discountAmount = validateCoupon(couponCode);
        
        if (discountAmount > 0) {
            updateDiscountAmount(discountAmount);
            showSuccessMessage(`쿠폰이 적용되었습니다. ${discountAmount.toLocaleString()}원 할인`);
            couponBtn.textContent = '적용됨';
            couponBtn.style.background = '#28a745';
            couponBtn.style.color = 'white';
        } else {
            showErrorMessage('유효하지 않은 쿠폰입니다.');
            couponBtn.textContent = originalText;
            couponBtn.disabled = false;
        }
    }, 1000);
}

function validateCoupon(couponCode) {
    const validCoupons = {
        'WELCOME10': 10000,
        'SAVE5000': 5000,
        'FIRST20': 20000
    };
    
    return validCoupons[couponCode] || 0;
}

function updateDiscountAmount(amount) {
    const discountElement = document.querySelector('.summary-row .summary-value');
    if (discountElement) {
        discountElement.textContent = `-${amount.toLocaleString()}원`;
    }
    
    calculateTotalAmount();
}

function setupAddressSearch() {
    const addressSearchBtn = document.querySelector('.address-search-btn');
    
    if (addressSearchBtn) {
        addressSearchBtn.addEventListener('click', function() {
            openAddressSearch();
        });
    }
}

function openAddressSearch() {
    const sampleAddress = {
        zipcode: '12345',
        address: '서울특별시 강남구 테헤란로 123',
        detail: ''
    };
    
    const zipcodeInput = document.querySelector('.postal-code-input');
    const addressInput = document.querySelector('.address-input');
    
    if (zipcodeInput) zipcodeInput.value = sampleAddress.zipcode;
    if (addressInput) addressInput.value = sampleAddress.address;
    
    showSuccessMessage('주소가 입력되었습니다.');
}

function setupFormValidation() {
    const inputs = document.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });
}

function setupDiscountSelection() {
    const discountSelect = document.querySelector('.discount-select');
    if (discountSelect) {
        discountSelect.addEventListener('change', function() {
            calculateTotalAmount();
        });
    }
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = '필수 입력 항목입니다.';
    }
    
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[0-9-+\s()]+$/;
        if (!phoneRegex.test(value)) {
            isValid = false;
            errorMessage = '올바른 연락처 형식이 아닙니다.';
        }
    }
    
    if (isValid) {
        field.classList.remove('error');
        removeErrorMessage(field);
    } else {
        field.classList.add('error');
        showErrorMessage(field, errorMessage);
    }
    
    return isValid;
}

function showErrorMessage(field, message) {
    removeErrorMessage(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function removeErrorMessage(field) {
    const existingError = field.parentNode.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
}

function calculateTotalAmount() {
    const paymentButton = document.getElementById('tossPaymentBtn');
    if (!paymentButton) {
        return;
    }
    
    let originalAmount = parseInt(paymentButton.getAttribute('data-original-amount')) || 0;
    if (originalAmount === 0) {
        originalAmount = parseInt(paymentButton.getAttribute('data-amount')) || 0;
        paymentButton.setAttribute('data-original-amount', originalAmount);
    }
    
    const discountAmount = getCurrentDiscountAmount();
    const finalAmount = originalAmount - discountAmount;
    
    const paymentText = paymentButton.querySelector('.payment-text');
    
    if (paymentText) {
        paymentText.textContent = `${finalAmount.toLocaleString()}원 결제하기`;
        paymentButton.setAttribute('data-amount', finalAmount);
    }
}

function getCurrentDiscountAmount() {
    const discountSelect = document.querySelector('.discount-select');
    if (discountSelect) {
        return parseInt(discountSelect.value) || 0;
    }
    return 0;
}

function processPayment() {
    if (!validateForm()) {
        showErrorMessage(null, '필수 정보를 모두 입력해주세요.');
        return;
    }
    
    const selectedPaymentMethod = document.querySelector('input[name="payment-method"]:checked');
    if (!selectedPaymentMethod) {
        showErrorMessage(null, '결제 방법을 선택해주세요.');
        return;
    }
    
    if (selectedPaymentMethod.value === 'card' && !window.selectedCardType) {
        showErrorMessage(null, '카드 종류를 선택해주세요.');
        return;
    }
    
    const paymentButton = document.getElementById('tossPaymentBtn');
    if (!paymentButton) {
        showErrorMessage(null, '결제 버튼을 찾을 수 없습니다.');
        return;
    }
    
    const discountAmount = getCurrentDiscountAmount();
    const totalAmount = parseInt(paymentButton.getAttribute('data-amount')) || 0;
    const finalAmount = totalAmount;
    
    if (!confirm(`${finalAmount.toLocaleString()}원을 결제하시겠습니까?`)) {
        return;
    }
    
    processPaymentRequest(selectedPaymentMethod.value, finalAmount);
}

function validateForm() {
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function processPaymentRequest(paymentMethod, amount) {
    const paymentButton = document.querySelector('.payment-button');
    const originalText = paymentButton.innerHTML;
    
    paymentButton.innerHTML = '<span>결제 처리 중...</span>';
    paymentButton.disabled = true;
        
    setTimeout(() => {
        const isSuccess = Math.random() > 0.1;
        
        if (isSuccess) {
            showSuccessMessage('결제가 완료되었습니다!');
            setTimeout(() => {
                window.location.href = '/orders/success/';
            }, 2000);
        } else {
            showErrorMessage(null, '결제 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
            paymentButton.innerHTML = originalText;
            paymentButton.disabled = false;
        }
    }, 2000);
}

function showSuccessMessage(message) {
    alert(message);
}

function showErrorMessage(element, message) {
    if (element) {
        showErrorMessage(element, message);
    } else {
        alert(message);
    }
}

function formatNumber(num) {
    return num.toLocaleString();
}

window.addEventListener('beforeunload', function(e) {
    const hasData = Array.from(document.querySelectorAll('input, select, textarea'))
        .some(field => field.value.trim() !== '');
    
    if (hasData) {
        e.preventDefault();
        e.returnValue = '입력한 정보가 사라집니다. 정말 나가시겠습니까?';
    }
});

function initializeTossPaymentWidget(paymentData, amount) {
    const clientKeyElement = document.getElementById('tossClientKey');
    const clientKey = clientKeyElement ? clientKeyElement.value : '';
    
    if (!clientKey) {
        alert('결제 시스템을 초기화할 수 없습니다. 클라이언트 키가 설정되지 않았습니다.');
        const paymentButton = document.getElementById('tossPaymentBtn');
        if (paymentButton) {
            const finalAmount = amount || 0;
            paymentButton.innerHTML = `<span class="payment-text">${finalAmount.toLocaleString()}원 결제하기</span>`;
            paymentButton.disabled = false;
        }
        return;
    }
    
    const tossPayments = TossPayments(clientKey);
    
    tossPayments.requestPayment('카드', {
        amount: amount,
        orderId: paymentData.orderId,
        orderName: paymentData.orderName,
        successUrl: paymentData.successUrl,
        failUrl: paymentData.failUrl,
        customerEmail: document.querySelector('.email-input')?.value || '',
        customerName: document.querySelector('.form-input[placeholder*="이름"]')?.value || '',
    })
    .catch(function (error) {
        const paymentButton = document.getElementById('tossPaymentBtn');
        const finalAmount = parseInt(paymentButton.getAttribute('data-amount')) || amount || 0;
        
        if (error.code === 'USER_CANCEL') {
            paymentButton.innerHTML = `<span class="payment-text">${finalAmount.toLocaleString()}원 결제하기</span>`;
            paymentButton.disabled = false;
        } else {
            alert('결제 요청 중 오류가 발생했습니다: ' + (error.message || '알 수 없는 오류'));
            paymentButton.innerHTML = `<span class="payment-text">${finalAmount.toLocaleString()}원 결제하기</span>`;
            paymentButton.disabled = false;
        }
    });
}

function setupTossPayment() {
    const tossPaymentBtn = document.getElementById('tossPaymentBtn');
    if (!tossPaymentBtn) {
        return;
    }
    
    tossPaymentBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        const orderId = tossPaymentBtn.getAttribute('data-order-id');
        const amount = parseInt(tossPaymentBtn.getAttribute('data-amount')) || 0;
        
        if (!orderId) {
            alert('주문 정보를 찾을 수 없습니다.');
            return;
        }
        
        if (amount <= 0) {
            alert('결제 금액이 올바르지 않습니다.');
            return;
        }
        
        requestTossPayment(orderId, amount);
    });
}

function requestTossPayment(orderId, amount) {
    const paymentButton = document.getElementById('tossPaymentBtn');
    const originalText = paymentButton.innerHTML;
    
    paymentButton.innerHTML = '<span class="payment-text">결제 요청 중...</span>';
    paymentButton.disabled = true;
    
    fetch('/payments/toss/request/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            orderId: orderId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const finalAmount = data.amount || amount;
            initializeTossPaymentWidget(data, finalAmount);
        } else {
            alert(data.error || '결제 요청에 실패했습니다.');
            paymentButton.innerHTML = originalText;
            paymentButton.disabled = false;
        }
    })
    .catch(error => {
        alert('결제 요청 중 오류가 발생했습니다.');
        paymentButton.innerHTML = originalText;
        paymentButton.disabled = false;
    });
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        return csrfToken.value;
    }
    
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    return '';
}
