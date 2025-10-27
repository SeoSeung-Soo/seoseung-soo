document.addEventListener('DOMContentLoaded', function() {
    const sphereContainer = document.querySelector('.review-sphere-container');
    const spheres = document.querySelectorAll('.review-sphere');
    const detailPanel = document.querySelector('.review-detail-panel');
    const closePanel = document.querySelector('.close-panel');
    
    if (!sphereContainer || !spheres.length) return;
    
    // 구체 위치 초기화 (3D 공간 배치)
    spheres.forEach((sphere, index) => {
        const angle = (index / spheres.length) * Math.PI * 2;
        const radius = Math.min(sphereContainer.offsetWidth, sphereContainer.offsetHeight) * 0.25;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        const z = (Math.random() - 0.5) * 200;
        
        sphere.style.left = `calc(50% + ${x}px)`;
        sphere.style.top = `calc(50% + ${y}px)`;
        sphere.style.setProperty('--z', z);
        sphere.dataset.index = index;
    });
    
    // 드래그 기능
    let dragging = false;
    let currentSphere = null;
    let offset = { x: 0, y: 0 };
    let lastX = 0;
    let lastY = 0;
    
    spheres.forEach(sphere => {
        // 마우스 이벤트
        sphere.addEventListener('mousedown', startDrag);
        sphere.addEventListener('touchstart', startDrag);
        
        // 클릭 이벤트
        sphere.addEventListener('click', function(e) {
            if (!dragging) {
                showReviewDetail(this.dataset.index);
            }
        });
    });
    
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag);
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
    
    function startDrag(e) {
        e.preventDefault();
        dragging = true;
        currentSphere = e.target.closest('.review-sphere');
        
        const rect = currentSphere.getBoundingClientRect();
        const containerRect = sphereContainer.getBoundingClientRect();
        
        if (e.type === 'mousedown') {
            offset.x = e.clientX - rect.left - rect.width / 2;
            offset.y = e.clientY - rect.top - rect.height / 2;
        } else {
            const touch = e.touches[0];
            offset.x = touch.clientX - rect.left - rect.width / 2;
            offset.y = touch.clientY - rect.top - rect.height / 2;
        }
        
        // 현재 구체의 위치를 lastX, lastY에 저장
        lastX = parseFloat(currentSphere.style.left) || 0;
        lastY = parseFloat(currentSphere.style.top) || 0;
        
        currentSphere.style.zIndex = '20';
        currentSphere.classList.add('dragging');
    }
    
    function drag(e) {
        if (!dragging || !currentSphere) return;
        
        e.preventDefault();
        const containerRect = sphereContainer.getBoundingClientRect();
        let clientX, clientY;
        
        if (e.type === 'mousemove') {
            clientX = e.clientX;
            clientY = e.clientY;
        } else {
            const touch = e.touches[0];
            clientX = touch.clientX;
            clientY = touch.clientY;
        }
        
        // 목표 위치 계산
        let targetX = clientX - containerRect.left - (currentSphere.offsetWidth / 2);
        let targetY = clientY - containerRect.top - (currentSphere.offsetHeight / 2);
        
        // 컨테이너 경계 내에서 제한
        targetX = Math.max(0, Math.min(containerRect.width - currentSphere.offsetWidth, targetX));
        targetY = Math.max(0, Math.min(containerRect.height - currentSphere.offsetHeight, targetY));
        
        // 부드러운 이동 (속도 조절: 데스크탑용 최적화)
        const speed = 0.4; // 0.3-0.5 사이가 부드럽고 빠름
        let x = lastX + (targetX - lastX) * speed;
        let y = lastY + (targetY - lastY) * speed;
        
        currentSphere.style.left = x + 'px';
        currentSphere.style.top = y + 'px';
        currentSphere.style.setProperty('--z', '0');
        
        lastX = x;
        lastY = y;
    }
    
    function endDrag(e) {
        if (!dragging || !currentSphere) return;
        
        currentSphere.style.zIndex = '';
        currentSphere.classList.remove('dragging');
        dragging = false;
        currentSphere = null;
    }
    
    function showReviewDetail(index) {
        // 모든 리뷰 내용 숨기기
        const reviewItems = document.querySelectorAll('.review-content-item');
        reviewItems.forEach(item => item.classList.remove('active'));
        
        // 선택된 리뷰 보이기
        const selectedReview = document.querySelector(`.review-content-item[data-review-index="${index}"]`);
        if (selectedReview) {
            selectedReview.classList.add('active');
            detailPanel.classList.add('active');
        }
        
        // 구체 선택 상태
        spheres.forEach((sphere, i) => {
            if (i == index) {
                sphere.classList.add('selected');
            } else {
                sphere.classList.remove('selected');
            }
        });
    }
    
    if (closePanel) {
        closePanel.addEventListener('click', function() {
            detailPanel.classList.remove('active');
            spheres.forEach(sphere => sphere.classList.remove('selected'));
        });
    }
    
    // 컨트롤 버튼 기능
    const autoRotateBtn = document.querySelector('.auto-rotate-btn');
    const resetBtn = document.querySelector('.reset-btn');
    
    let autoRotateInterval = null;
    
    if (autoRotateBtn) {
        autoRotateBtn.addEventListener('click', function() {
            if (autoRotateInterval) {
                clearInterval(autoRotateInterval);
                autoRotateInterval = null;
                this.textContent = '자동 회전';
                spheres.forEach(sphere => sphere.style.transition = 'all 0.3s ease');
            } else {
                this.textContent = '정지';
                spheres.forEach(sphere => sphere.style.transition = 'none');
                
                autoRotateInterval = setInterval(() => {
                    spheres.forEach((sphere, index) => {
                        const currentLeft = parseFloat(sphere.style.left) || 0;
                        const currentTop = parseFloat(sphere.style.top) || 0;
                        const angle = (index / spheres.length) * Math.PI * 2 + (Date.now() * 0.001);
                        const radius = Math.min(sphereContainer.offsetWidth, sphereContainer.offsetHeight) * 0.25;
                        const x = Math.cos(angle) * radius;
                        const y = Math.sin(angle) * radius;
                        
                        sphere.style.left = `calc(50% + ${x}px)`;
                        sphere.style.top = `calc(50% + ${y}px)`;
                    });
                }, 16);
            }
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (autoRotateInterval) {
                clearInterval(autoRotateInterval);
                autoRotateInterval = null;
                if (autoRotateBtn) {
                    autoRotateBtn.textContent = '자동 회전';
                }
            }
            
            spheres.forEach((sphere, index) => {
                sphere.style.transition = 'all 0.5s ease';
                const angle = (index / spheres.length) * Math.PI * 2;
                const radius = Math.min(sphereContainer.offsetWidth, sphereContainer.offsetHeight) * 0.25;
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;
                
                sphere.style.left = `calc(50% + ${x}px)`;
                sphere.style.top = `calc(50% + ${y}px)`;
                sphere.style.setProperty('--z', '0');
                sphere.classList.remove('selected');
            });
            
            detailPanel.classList.remove('active');
            
            setTimeout(() => {
                spheres.forEach(sphere => sphere.style.transition = 'all 0.3s ease');
            }, 500);
        });
    }
});
