document.addEventListener('DOMContentLoaded', function() {
    initializePaymentPage();
});

function initializePaymentPage() {
    setupPaymentMethodSelection();
    setupCouponApplication();
    setupAddressSearch();
    setupFormValidation();
    setupDiscountSelection();
    calculateTotalAmount();
    setupDropdownCloseOnOutsideClick();
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
            
            // 신용카드인 경우 드롭다운 표시
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

function updateSelectedCardDisplay(cardName) {
    const paymentMethod = document.querySelector('.payment-method.selected');
    const methodDesc = paymentMethod.querySelector('.payment-method-desc');
    
    if (methodDesc) {
        methodDesc.textContent = cardName;
    }
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

// 쿠폰 적용 기능
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
    const productAmount = 51210;
    const shippingFee = 0;
    const discountAmount = getCurrentDiscountAmount();
    
    const totalAmount = productAmount + shippingFee - discountAmount;
    
    const paymentButton = document.querySelector('.payment-button .payment-text');
    
    if (paymentButton) {
        paymentButton.textContent = `${totalAmount.toLocaleString()}원 결제하기`;
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
    
    const discountAmount = getCurrentDiscountAmount();
    const finalAmount = 51210 - discountAmount;
    
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
