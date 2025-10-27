// 상품 이미지 변경 기능
function changeMainImage(imageUrl) {
    document.getElementById('mainImage').src = imageUrl;
    
    const thumbnails = document.querySelectorAll('.thumbnail');
    thumbnails.forEach(thumbnail => {
        thumbnail.classList.remove('active');
    });
    
    const clickedThumbnail = document.querySelector(`.thumbnail[src="${imageUrl}"]`);
    if (clickedThumbnail) {
        clickedThumbnail.classList.add('active');
    }
}

function increaseQuantity() {
    const quantityDisplay = document.getElementById('quantityDisplay');
    const cartQuantity = document.getElementById('cartQuantity');
    const productStock = document.querySelector('.size-quantity-section').dataset.productStock;
    let currentQuantity = parseInt(quantityDisplay.textContent);
    
    if (currentQuantity < parseInt(productStock)) {
        currentQuantity++;
        quantityDisplay.textContent = currentQuantity;
        cartQuantity.value = currentQuantity;
    } else {
        alert('재고가 부족합니다.');
    }
}

function decreaseQuantity() {
    const quantityDisplay = document.getElementById('quantityDisplay');
    const cartQuantity = document.getElementById('cartQuantity');
    let currentQuantity = parseInt(quantityDisplay.textContent);
    
    if (currentQuantity > 1) {
        currentQuantity--;
        quantityDisplay.textContent = currentQuantity;
        cartQuantity.value = currentQuantity;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('.comment-input-wrapper textarea');
    
    textareas.forEach(function(textarea) {
        const charCount = textarea.parentElement.querySelector('.char-count');
        
        if (charCount) {
            function updateCharCount() {
                const count = textarea.value.length;
                charCount.textContent = count;
                
                if (count > 450) {
                    charCount.style.color = '#ef4444';
                } else if (count > 400) {
                    charCount.style.color = '#f59e0b';
                } else {
                    charCount.style.color = '#374151';
                }
            }
            
            textarea.addEventListener('input', updateCharCount);
            updateCharCount();
        }
    });
    
    const cartForm = document.querySelector('.cart-form');
    if (cartForm) {
        cartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const quantityDisplay = document.getElementById('quantityDisplay');
            const cartQuantity = document.getElementById('cartQuantity');
            
            if (quantityDisplay && cartQuantity) {
                cartQuantity.value = quantityDisplay.textContent;
            }
            
            const formData = new FormData(cartForm);
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(cartForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Network response was not ok');
            })
            .then(data => {
                if (data.success) {
                    toast.success(data.message, '장바구니 담기');
                } else {
                    toast.error(data.message, '오류');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                toast.error('장바구니 추가 중 오류가 발생했습니다.', '오류');
            });
        });
    }
});

function editComment(commentId) {
    const commentItem = document.getElementById(`comment-${commentId}`);
    const commentContent = commentItem.querySelector('.comment-content');
    const editForm = document.getElementById(`edit-form-${commentId}`);
    const editTextarea = document.getElementById(`edit-textarea-${commentId}`);
    const charCount = document.getElementById(`edit-char-count-${commentId}`);
    
    commentContent.style.display = 'none';
    editForm.style.display = 'block';
    
    editTextarea.focus();
    
    function updateCharCount() {
        const count = editTextarea.value.length;
        charCount.textContent = count;
        
        if (count > 450) {
            charCount.style.color = '#ef4444';
        } else if (count > 400) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#374151';
        }
    }
    
    editTextarea.addEventListener('input', updateCharCount);
    updateCharCount();
}

function cancelEditComment(commentId) {
    const commentItem = document.getElementById(`comment-${commentId}`);
    const commentContent = commentItem.querySelector('.comment-content');
    const editForm = document.getElementById(`edit-form-${commentId}`);
    const editTextarea = document.getElementById(`edit-textarea-${commentId}`);
    const editIsPublished = document.getElementById(`edit-is-published-${commentId}`);
    
    const originalContent = commentContent.dataset.content;
    const originalIsPublished = commentContent.dataset.isPublished === 'true';
    
    editTextarea.value = originalContent;
    editIsPublished.checked = originalIsPublished;
    
    editForm.style.display = 'none';
    commentContent.style.display = 'block';
}

function saveComment(commentId) {
    const editTextarea = document.getElementById(`edit-textarea-${commentId}`);
    const editIsPublished = document.getElementById(`edit-is-published-${commentId}`);
    const content = editTextarea.value.trim();
    
    if (content.length < 1) {
        alert('댓글 내용을 입력해주세요.');
        return;
    }
    
    if (content.length > 500) {
        alert('댓글은 최대 500자까지 입력 가능합니다.');
        return;
    }
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/reviews/comment/update/${commentId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            content: content,
            is_published: editIsPublished.checked
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commentItem = document.getElementById(`comment-${commentId}`);
            const commentContent = commentItem.querySelector('.comment-content');
            const editForm = document.getElementById(`edit-form-${commentId}`);
            
            commentContent.dataset.content = data.comment.content;
            commentContent.dataset.isPublished = data.comment.is_published;
            
            commentContent.textContent = data.comment.content;
            
            editForm.style.display = 'none';
            commentContent.style.display = 'block';
            
            alert('댓글이 수정되었습니다.');
        } else {
            alert(data.error || '댓글 수정에 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('댓글 수정 중 오류가 발생했습니다.');
    });
}

function editReview(reviewId) {
    const reviewText = document.getElementById(`review-text-${reviewId}`);
    const editForm = document.getElementById(`review-edit-form-${reviewId}`);
    const editTextarea = document.getElementById(`review-edit-textarea-${reviewId}`);
    const charCount = document.getElementById(`review-edit-char-count-${reviewId}`);
    
    reviewText.style.display = 'none';
    editForm.style.display = 'block';
    
    editTextarea.focus();
    
    function updateCharCount() {
        const count = editTextarea.value.length;
        charCount.textContent = count;
        
        if (count > 900) {
            charCount.style.color = '#ef4444';
        } else if (count > 800) {
            charCount.style.color = '#f59e0b';
        } else {
            charCount.style.color = '#374151';
        }
    }
    
    editTextarea.addEventListener('input', updateCharCount);
    updateCharCount();
}

function cancelEditReview(reviewId) {
    const reviewText = document.getElementById(`review-text-${reviewId}`);
    const editForm = document.getElementById(`review-edit-form-${reviewId}`);
    const editTextarea = document.getElementById(`review-edit-textarea-${reviewId}`);
    
    const originalContent = reviewText.dataset.content;
    const originalRating = reviewText.dataset.rating;
    
    editTextarea.value = originalContent;
    
    const ratingInput = document.querySelector(`input[name="rating-edit-${reviewId}"][value="${originalRating}"]`);
    if (ratingInput) {
        ratingInput.checked = true;
    }
    
    editForm.style.display = 'none';
    reviewText.style.display = 'block';
}

function saveReview(reviewId) {
    const editTextarea = document.getElementById(`review-edit-textarea-${reviewId}`);
    const content = editTextarea.value.trim();
    const ratingInput = document.querySelector(`input[name="rating-edit-${reviewId}"]:checked`);
    
    if (!ratingInput) {
        alert('평점을 선택해주세요.');
        return;
    }
    
    const rating = parseInt(ratingInput.value);
    
    if (content.length < 10) {
        alert('리뷰 내용을 최소 10자 이상 입력해주세요.');
        return;
    }
    
    if (content.length > 1000) {
        alert('리뷰는 최대 1000자까지 입력 가능합니다.');
        return;
    }
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/reviews/update/${reviewId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            content: content,
            rating: rating
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const reviewText = document.getElementById(`review-text-${reviewId}`);
            const reviewRating = document.getElementById(`review-rating-${reviewId}`);
            const editForm = document.getElementById(`review-edit-form-${reviewId}`);
            
            reviewText.dataset.content = data.review.content;
            reviewText.dataset.rating = data.review.rating;
            
            reviewText.textContent = data.review.content;
            reviewRating.textContent = data.review.star_display;
            
            editForm.style.display = 'none';
            reviewText.style.display = 'block';
            
            alert('리뷰가 수정되었습니다.');
        } else {
            alert(data.error || '리뷰 수정에 실패했습니다.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('리뷰 수정 중 오류가 발생했습니다.');
    });
}