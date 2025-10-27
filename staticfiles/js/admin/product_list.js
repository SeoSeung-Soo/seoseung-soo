document.addEventListener('DOMContentLoaded', () => {
  // 필터 기능
  const filterSelect = document.querySelector('.filter-select');
  const productCards = document.querySelectorAll('.product-card');
  
  if (filterSelect) {
    filterSelect.addEventListener('change', (e) => {
      const filterValue = e.target.value;
      
      productCards.forEach(card => {
        const status = card.getAttribute('data-status');
        
        if (filterValue === '' || status === filterValue) {
          card.style.display = 'block';
          card.classList.remove('hidden');
        } else {
          card.style.display = 'none';
          card.classList.add('hidden');
        }
      });
    });
  }
  
  // 상품 카드 호버 효과
  productCards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'translateY(0)';
    });
  });
});

// 상품 삭제 확인
function deleteProduct(productId) {
  if (confirm('이 상품을 삭제하시겠습니까?\n삭제된 상품은 복구할 수 없습니다.')) {
    // AJAX 요청으로 상품 삭제
    fetch(`/admin/products/${productId}/delete/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      },
    })
    .then(response => {
      if (response.ok) {
        // 성공 시 페이지 새로고침 또는 카드 제거
        location.reload();
      } else {
        alert('상품 삭제에 실패했습니다.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('오류가 발생했습니다.');
    });
  }
}

// 검색 기능 (필요시 추가)
function searchProducts(query) {
  const productCards = document.querySelectorAll('.product-card');
  
  productCards.forEach(card => {
    const productName = card.querySelector('.product-name').textContent.toLowerCase();
    const productDescription = card.querySelector('.product-description').textContent.toLowerCase();
    const searchQuery = query.toLowerCase();
    
    if (productName.includes(searchQuery) || productDescription.includes(searchQuery)) {
      card.style.display = 'block';
      card.classList.remove('hidden');
    } else {
      card.style.display = 'none';
      card.classList.add('hidden');
    }
  });
}
