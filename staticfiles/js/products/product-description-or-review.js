// 탭 기능
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // 모든 탭 버튼에서 active 클래스 제거
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // 모든 탭 패널에서 active 클래스 제거
            tabPanels.forEach(panel => panel.classList.remove('active'));
            
            // 클릭된 버튼에 active 클래스 추가
            this.classList.add('active');
            
            // 해당 탭 패널에 active 클래스 추가
            const targetPanel = document.getElementById(targetTab);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
});

// 사진 업로드 기능
document.addEventListener('DOMContentLoaded', function() {
    const uploadBox = document.getElementById('uploadBox');
    const photoInput = document.getElementById('photoInput');
    const uploadedPhoto = document.getElementById('uploadedPhoto');
    const previewImage = document.getElementById('previewImage');
    const photoName = document.getElementById('photoName');
    const photoSize = document.getElementById('photoSize');
    const removePhoto = document.getElementById('removePhoto');
    const aiProcessSection = document.getElementById('aiProcessSection');
    const aiProcessBtn = document.getElementById('aiProcessBtn');
    const aiResultSection = document.getElementById('aiResultSection');
    
    // 파일 업로드 박스 클릭
    if (uploadBox) {
        uploadBox.addEventListener('click', function() {
            photoInput.click();
        });
    }
    
    // 드래그 앤 드롭 기능
    if (uploadBox) {
        uploadBox.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadBox.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        uploadBox.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
    }
    
    // 파일 선택
    if (photoInput) {
        photoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFileUpload(file);
            }
        });
    }
    
    // 파일 업로드 처리
    function handleFileUpload(file) {
        // 파일 타입 검증
        if (!file.type.startsWith('image/')) {
            alert('이미지 파일만 업로드 가능합니다.');
            return;
        }
        
        // 파일 크기 검증 (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('파일 크기는 10MB 이하여야 합니다.');
            return;
        }
        
        // 파일 읽기
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            photoName.textContent = file.name;
            photoSize.textContent = formatFileSize(file.size);
            
            // 업로드 박스 숨기고 미리보기 표시
            uploadBox.style.display = 'none';
            uploadedPhoto.style.display = 'block';
            aiProcessSection.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
    
    // 파일 크기 포맷팅
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 사진 제거
    if (removePhoto) {
        removePhoto.addEventListener('click', function() {
            uploadBox.style.display = 'block';
            uploadedPhoto.style.display = 'none';
            aiProcessSection.style.display = 'none';
            aiResultSection.style.display = 'none';
            photoInput.value = '';
        });
    }
    
    // AI 가상 피팅 시작
    if (aiProcessBtn) {
        aiProcessBtn.addEventListener('click', function() {
            // 로딩 상태 표시
            const btnText = this.querySelector('.btn-text');
            const originalText = btnText.textContent;
            btnText.innerHTML = '<span class="loading"></span> AI 분석 중...';
            this.disabled = true;
            
            // 실제 구현에서는 AI API 호출
            setTimeout(() => {
                // 임시 결과 표시
                showAIResult();
                
                // 버튼 원상복구
                btnText.textContent = originalText;
                this.disabled = false;
            }, 3000);
        });
    }
    
    // AI 결과 표시
    function showAIResult() {
        aiProcessSection.style.display = 'none';
        aiResultSection.style.display = 'block';
        
        // 임시 결과 이미지 (실제로는 AI API에서 받은 결과)
        const originalResult = document.getElementById('originalResult');
        const fittingResult = document.getElementById('fittingResult');
        
        originalResult.src = previewImage.src;
        fittingResult.src = previewImage.src; // 실제로는 AI 처리된 이미지
        
        // 결과 섹션으로 스크롤
        aiResultSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 다시 시도 버튼
    const retryBtn = document.querySelector('.retry-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', function() {
            aiResultSection.style.display = 'none';
            aiProcessSection.style.display = 'block';
        });
    }
    
    // 다운로드 버튼
    const downloadBtn = document.querySelector('.download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            // 실제 구현에서는 처리된 이미지 다운로드
            alert('다운로드 기능은 준비 중입니다.');
        });
    }
});