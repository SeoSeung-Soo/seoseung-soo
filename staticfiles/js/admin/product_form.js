document.addEventListener('DOMContentLoaded', () => {
  // 이미지 미리보기
  const fileInput = document.querySelector('.form-file');
  const imageGrid = document.querySelector('.image-grid');
  
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const files = Array.from(e.target.files);
      
      files.forEach(file => {
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (e) => {
            const imageItem = document.createElement('div');
            imageItem.className = 'image-item';
            imageItem.innerHTML = `
              <img src="${e.target.result}" alt="미리보기" class="preview-image">
              <button type="button" class="remove-image-btn" onclick="removePreviewImage(this)">×</button>
            `;
            
            if (!imageGrid) {
              const existingImages = document.querySelector('.existing-images');
              if (existingImages) {
                existingImages.appendChild(imageItem);
              } else {
                const newImageSection = document.createElement('div');
                newImageSection.className = 'existing-images';
                newImageSection.innerHTML = '<h3 class="sub-title">업로드할 이미지</h3>';
                newImageSection.appendChild(imageItem);
                document.querySelector('.form-section:last-child').appendChild(newImageSection);
              }
            } else {
              imageGrid.appendChild(imageItem);
            }
          };
          reader.readAsDataURL(file);
        }
      });
    });
  }
  
  // 폼 유효성 검사
  const form = document.querySelector('.product-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      const requiredFields = form.querySelectorAll('[required]');
      let isValid = true;
      
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          field.classList.add('error');
          isValid = false;
        } else {
          field.classList.remove('error');
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        alert('필수 항목을 모두 입력해주세요.');
      }
    });
  }
});

// 미리보기 이미지 제거
function removePreviewImage(button) {
  button.parentElement.remove();
}

// 기존 이미지 제거 (AJAX)
function removeExistingImage(imageId) {
  if (confirm('이 이미지를 삭제하시겠습니까?')) {
    // AJAX 요청으로 이미지 삭제
    fetch(`/products/admin/image/${imageId}/delete/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // 성공 시 해당 이미지 요소 제거
        const imageElement = document.querySelector(`[data-image-id="${imageId}"]`);
        if (imageElement) {
          imageElement.parentElement.remove();
        }
        alert(data.message);
      } else {
        alert(data.message || '이미지 삭제에 실패했습니다.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('오류가 발생했습니다.');
    });
  }
}

