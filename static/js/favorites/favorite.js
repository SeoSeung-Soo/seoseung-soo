function addToCart(productId) {
    fetch('/carts/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('장바구니에 추가되었습니다.');
        } else {
            alert('오류: ' + data.message);
        }
    })
    .catch(error => {
        alert('장바구니 추가 중 오류가 발생했습니다.');
    });
}

function addToWishlist(productId) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    fetch('/favorites/create/', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateWishlistButton(productId, data.is_favorite);
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('찜하기 처리 중 오류가 발생했습니다.', 'error');
    });
}

function removeFavorite(favoriteId) {
    if (confirm('찜목록에서 제거하시겠습니까?')) {
        const formData = new FormData();
        formData.append('favorite_id', favoriteId);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        fetch('/favorites/delete/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 찜한 상품 요소를 DOM에서 제거
                const favoriteItem = document.querySelector(`button[onclick="removeFavorite(${favoriteId})"]`).closest('.favorite-item');
                if (favoriteItem) {
                    favoriteItem.remove();
                }
                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('찜 해제 중 오류가 발생했습니다.', 'error');
        });
    }
}

function updateWishlistButton(productId, isFavorite) {
    const button = document.getElementById(`wishlist-btn-${productId}`);
    if (button) {
        if (isFavorite) {
            button.textContent = '찜하기 취소';
        } else {
            button.textContent = '찜하기';
        }
    }
    
    const drawerWishlistBtn = document.getElementById('drawerWishlistBtn');
    if (drawerWishlistBtn) {
        drawerWishlistBtn.textContent = isFavorite ? '★' : '☆';
    }
}

function showToast(message, type = 'info') {
    if (typeof toast !== 'undefined') {
        if (type === 'success') {
            toast.success(message, '찜하기');
        } else if (type === 'error') {
            toast.error(message, '찜하기');
        } else {
            toast.info(message, '찜하기');
        }
    } else {
        alert(message);
    }
}