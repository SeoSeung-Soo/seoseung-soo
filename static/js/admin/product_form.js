document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.querySelector('input[type="file"]');
  const imageGrid = document.querySelector('.image-grid');
  let selectedFiles = [];
  
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const newFiles = Array.from(e.target.files);
      
      selectedFiles = [...selectedFiles, ...newFiles];
      
      let existingImages = document.querySelector('.existing-images');
      if (!imageGrid && !existingImages) {
        const newImageSection = document.createElement('div');
        newImageSection.className = 'existing-images';
        newImageSection.innerHTML = '<h3 class="sub-title">업로드할 이미지</h3>';
        
        const lastFormSection = document.querySelector('.form-section:last-child');
        if (lastFormSection) {
          lastFormSection.appendChild(newImageSection);
        } else {
          document.body.appendChild(newImageSection);
        }
        existingImages = newImageSection;
      }

      newFiles.forEach(file => {
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = (e) => {
            const imageItem = document.createElement('div');
            imageItem.className = 'image-item';
            imageItem.innerHTML = `
              <img src="${e.target.result}" alt="미리보기" class="preview-image">
              <button type="button" class="remove-image-btn" onclick="removePreviewImage(this, '${file.name}')">×</button>
            `;
            
            if (imageGrid) {
              imageGrid.appendChild(imageItem);
            } else {
              existingImages.appendChild(imageItem);
            }
          };
          reader.readAsDataURL(file);
        }
      });
    });
  }
  
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
        return;
      }
      
      if (selectedFiles.length > 0) {
        const formData = new FormData(form);
        
        const existingFileInput = form.querySelector('input[type="file"]');
        if (existingFileInput) {
          existingFileInput.remove();
        }
        
        const newFileInput = document.createElement('input');
        newFileInput.type = 'file';
        newFileInput.name = 'image';
        newFileInput.multiple = true;
        newFileInput.style.display = 'none';
        
        const dt = new DataTransfer();
        selectedFiles.forEach(file => dt.items.add(file));
        newFileInput.files = dt.files;
        
        form.appendChild(newFileInput);
        
      }
    });
  }
});

function removePreviewImage(button, fileName) {
  selectedFiles = selectedFiles.filter(file => file.name !== fileName);
  
  button.parentElement.remove();
}

function removeExistingImage(imageId) {
  if (confirm('이 이미지를 삭제하시겠습니까?')) {
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
      alert('오류가 발생했습니다.');
    });
  }
}

