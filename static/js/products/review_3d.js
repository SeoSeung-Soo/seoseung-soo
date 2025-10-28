document.addEventListener('DOMContentLoaded', function() {
    const sphereContainer = document.querySelector('.review-sphere-container');
    const spheres = document.querySelectorAll('.review-sphere');
    const detailPanel = document.querySelector('.review-detail-panel');
    const closePanel = document.querySelector('.close-panel');
    
    if (!sphereContainer || !spheres.length) return;
    
    // 상수 (반응형)
    const isMobile = window.innerWidth <= 768;
    const SPHERE_RADIUS = isMobile ? 15 : 20; // 모바일: 30px / 2, 데스크탑: 40px / 2
    const MIN_DISTANCE = SPHERE_RADIUS * 2 + 5; // 구체 간 최소 거리
    const HORIZONTAL_PADDING = isMobile ? 20 : 100; // 모바일: 20px, 데스크탑: 100px
    
    // 드래그 상태
    let selectedSphere = null;
    let offsetX = 0;
    let offsetY = 0;
    let isDragging = false;
    
    // 컨테이너 크기 (동적으로 가져오기)
    function getContainerSize() {
        return {
            width: sphereContainer.offsetWidth,
            height: sphereContainer.offsetHeight
        };
    }
    
    // 초기 위치 설정 (랜덤 배치)
    function initializeSpheres() {
        const { width, height } = getContainerSize();   
        
        // 컨테이너 크기가 0이면 잠시 대기 후 재시도
        if (width === 0 || height === 0) {
            console.log('Container not ready, retrying...');
            setTimeout(initializeSpheres, 100);
            return;
        }
        
        const positions = []; // 이미 배치된 위치들
        
        spheres.forEach((sphere, index) => {
            let x, y;
            let attempts = 0;
            const maxAttempts = 100;
            
            // 겹치지 않는 랜덤 위치 찾기
            do {
                x = HORIZONTAL_PADDING + Math.random() * (width - SPHERE_RADIUS * 2 - HORIZONTAL_PADDING * 2);
                y = Math.random() * (height - SPHERE_RADIUS * 2);
                attempts++;
            } while (isOverlapping(x, y, positions) && attempts < maxAttempts);
            
            // 위치 저장
            positions.push({ x, y });
            
            sphere.style.left = `${x}px`;
            sphere.style.top = `${y}px`;
            sphere.dataset.index = index;
        });
    }
    
    // 겹침 체크 함수
    function isOverlapping(x, y, positions) {
        for (let pos of positions) {
            const dx = (x + SPHERE_RADIUS) - (pos.x + SPHERE_RADIUS);
            const dy = (y + SPHERE_RADIUS) - (pos.y + SPHERE_RADIUS);
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < MIN_DISTANCE) {
                return true;
            }
        }
        return false;
    }
    
    // 약간의 지연 후 초기화 (CSS 렌더링 대기)
    setTimeout(initializeSpheres, 100);
    
    // 마우스 다운 이벤트
    spheres.forEach(sphere => {
        sphere.addEventListener('mousedown', e => {
            e.preventDefault();
            selectedSphere = sphere;
            isDragging = false;
            
            const rect = sphere.getBoundingClientRect();
            const containerRect = sphereContainer.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            
            sphere.style.zIndex = '20';
            sphere.classList.add('dragging');
        });
        
        sphere.addEventListener('touchstart', e => {
            e.preventDefault();
            const touch = e.touches[0];
            selectedSphere = sphere;
            isDragging = false;
            
            const rect = sphere.getBoundingClientRect();
            offsetX = touch.clientX - rect.left;
            offsetY = touch.clientY - rect.top;
            
            sphere.style.zIndex = '20';
            sphere.classList.add('dragging');
        }, { passive: false });
        
        // 클릭/터치 이벤트 (드래그하지 않았을 때만)
        const handleSphereClick = function(e) {
            if (!isDragging) {
                const reviewId = parseInt(this.dataset.reviewId);
                showReviewModal(reviewId);
            }
        };
        
        sphere.addEventListener('click', handleSphereClick);
        sphere.addEventListener('touchend', function(e) {
            if (!isDragging) {
                e.preventDefault();
                handleSphereClick.call(this, e);
            }
        }, { passive: false });
    });
    
    // 마우스 이동 이벤트
    document.addEventListener('mousemove', e => {
        if (!selectedSphere) return;
        e.preventDefault();
        isDragging = true;
        
        const { width, height } = getContainerSize();
        const containerRect = sphereContainer.getBoundingClientRect();
        let x = e.clientX - containerRect.left - offsetX;
        let y = e.clientY - containerRect.top - offsetY;
        
        // 컨테이너 경계 제한 (좌우 패딩 적용)
        x = Math.max(HORIZONTAL_PADDING, Math.min(width - SPHERE_RADIUS * 2 - HORIZONTAL_PADDING, x));
        y = Math.max(0, Math.min(height - SPHERE_RADIUS * 2, y));
        
        selectedSphere.style.left = `${x}px`;
        selectedSphere.style.top = `${y}px`;
        
        // 충돌 감지
        checkCollision(selectedSphere);
    });
    
    document.addEventListener('touchmove', e => {
        if (!selectedSphere) return;
        e.preventDefault();
        isDragging = true;
        
        const { width, height } = getContainerSize();
        const touch = e.touches[0];
        const containerRect = sphereContainer.getBoundingClientRect();
        let x = touch.clientX - containerRect.left - offsetX;
        let y = touch.clientY - containerRect.top - offsetY;
        
        // 컨테이너 경계 제한 (좌우 패딩 적용)
        x = Math.max(HORIZONTAL_PADDING, Math.min(width - SPHERE_RADIUS * 2 - HORIZONTAL_PADDING, x));
        y = Math.max(0, Math.min(height - SPHERE_RADIUS * 2, y));
        
        selectedSphere.style.left = `${x}px`;
        selectedSphere.style.top = `${y}px`;
        
        // 충돌 감지
        checkCollision(selectedSphere);
    }, { passive: false });
    
    // 마우스 업 이벤트
    document.addEventListener('mouseup', () => {
        if (selectedSphere) {
            selectedSphere.style.zIndex = '';
            selectedSphere.classList.remove('dragging');
            selectedSphere = null;
        }
    });
    
    document.addEventListener('touchend', () => {
        if (selectedSphere) {
            selectedSphere.style.zIndex = '';
            selectedSphere.classList.remove('dragging');
            selectedSphere = null;
        }
        // 짧은 지연 후 isDragging 리셋 (터치 클릭 감지를 위해)
        setTimeout(() => {
            isDragging = false;
        }, 100);
    });
    
    // 충돌 감지 및 처리
    function checkCollision(currentSphere) {
        const { width, height } = getContainerSize();
        const rect1 = currentSphere.getBoundingClientRect();
        const containerRect = sphereContainer.getBoundingClientRect();
        const r1 = SPHERE_RADIUS;
        const x1 = rect1.left - containerRect.left + r1;
        const y1 = rect1.top - containerRect.top + r1;
        
        spheres.forEach(otherSphere => {
            if (otherSphere === currentSphere) return;
            
            const rect2 = otherSphere.getBoundingClientRect();
            const r2 = SPHERE_RADIUS;
            const x2 = rect2.left - containerRect.left + r2;
            const y2 = rect2.top - containerRect.top + r2;
            
            const dx = x2 - x1;
            const dy = y2 - y1;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < MIN_DISTANCE && distance > 0) {
                // 겹쳤을 때 -> 다른 구체만 밀어냄
                const overlap = MIN_DISTANCE - distance;
                const angle = Math.atan2(dy, dx);
                const moveX = overlap * Math.cos(angle);
                const moveY = overlap * Math.sin(angle);
                
                // 다른 구체를 GSAP로 부드럽게 이동
                const otherX = parseFloat(otherSphere.style.left || 0) + moveX;
                const otherY = parseFloat(otherSphere.style.top || 0) + moveY;
                
                // 경계 체크 (좌우 패딩 적용)
                const boundedX = Math.max(HORIZONTAL_PADDING, Math.min(width - SPHERE_RADIUS * 2 - HORIZONTAL_PADDING, otherX));
                const boundedY = Math.max(0, Math.min(height - SPHERE_RADIUS * 2, otherY));
                
                gsap.to(otherSphere, {
                    left: boundedX,
                    top: boundedY,
                    duration: 0.2,
                    ease: 'power2.out'
                });
            }
        });
    }
    
    // 모달 관련 변수
    const reviewModal = document.getElementById('reviewModal');
    const modalClose = document.querySelector('.modal-close');
    const modalOverlay = document.querySelector('.modal-overlay');
    const modalImages = document.getElementById('modalImages');
    const modalAvatar = document.getElementById('modalAvatar');
    const modalUsername = document.getElementById('modalUsername');
    const modalRating = document.getElementById('modalRating');
    const modalReviewText = document.getElementById('modalReviewText');
    const modalDate = document.getElementById('modalDate');
    const modalPrev = document.getElementById('modalPrev');
    const modalNext = document.getElementById('modalNext');
    
    // 모달 요소가 없으면 종료
    if (!reviewModal || !modalImages || !modalAvatar || !modalUsername || !modalRating || !modalReviewText || !modalDate) {
    }
    
    // 모달이 없으면 함수 종료
    if (!reviewModal) {
        return;
    }
    
    // 현재 리뷰 ID 추적
    let currentReviewIndex = 0;
    let currentReviewId = null;
    let sliderCurrentIndex = 0; // 이미지 슬라이더 인덱스
    let slideInterval = null; // 슬라이드쇼 인터벌
    
    // 다음 리뷰로 이동 (디바운스 적용)
    let nextReviewTimeout;
    function showNextReview() {
        if (!window.reviewData || window.reviewData.length === 0) return;
        
        clearTimeout(nextReviewTimeout);
        nextReviewTimeout = setTimeout(() => {
            const nextIndex = (currentReviewIndex + 1) % window.reviewData.length;
            currentReviewIndex = nextIndex;
            sliderCurrentIndex = 0; // 슬라이더 인덱스 초기화
            showReviewModal(window.reviewData[nextIndex].id);
            updateNavButtons();
        }, 100);
    }
    
    // 이전 리뷰로 이동 (디바운스 적용)
    let prevReviewTimeout;
    function showPrevReview() {
        if (!window.reviewData || window.reviewData.length === 0) return;
        
        clearTimeout(prevReviewTimeout);
        prevReviewTimeout = setTimeout(() => {
            const prevIndex = (currentReviewIndex - 1 + window.reviewData.length) % window.reviewData.length;
            currentReviewIndex = prevIndex;
            sliderCurrentIndex = 0; // 슬라이더 인덱스 초기화
            showReviewModal(window.reviewData[prevIndex].id);
            updateNavButtons();
        }, 100);
    }
    
    // 네비게이션 버튼 상태 업데이트
    function updateNavButtons() {
        if (!window.reviewData || window.reviewData.length === 0) return;
        
        // 첫 번째/마지막 리뷰인지 확인
        const isFirst = currentReviewIndex === 0;
        const isLast = currentReviewIndex === window.reviewData.length - 1;
        
        if (modalPrev) {
            if (window.reviewData.length === 1) {
                modalPrev.style.display = 'none';
            } else {
                modalPrev.style.display = 'flex';
                modalPrev.style.opacity = isFirst ? '0.3' : '1';
            }
        }
        
        if (modalNext) {
            if (window.reviewData.length === 1) {
                modalNext.style.display = 'none';
            } else {
                modalNext.style.display = 'flex';
                modalNext.style.opacity = isLast ? '0.3' : '1';
            }
        }
    }
    
    // 리뷰 모달 열기
    function showReviewModal(reviewId) {
        // 이전 타이머 정리
        if (slideInterval) {
            clearInterval(slideInterval);
            slideInterval = null;
        }
        
        if (!window.reviewData || window.reviewData.length === 0) {
            return;
        }
        
        const review = window.reviewData.find(r => r.id === reviewId);
        if (!review) {
            return;
        }
        
        // 현재 리뷰 인덱스 저장
        currentReviewIndex = window.reviewData.findIndex(r => r.id === reviewId);
        currentReviewId = reviewId;
        
        // 아바타 설정
        modalAvatar.innerHTML = '';
        if (review.hasProfileImage && review.profileImage) {
            const img = document.createElement('img');
            img.src = review.profileImage;
            img.alt = review.username;
            modalAvatar.appendChild(img);
        } else {
            modalAvatar.textContent = 'S';
        }
        
        // 사용자 정보 설정
        modalUsername.textContent = review.username;
        modalRating.textContent = review.rating;
        modalReviewText.textContent = review.content;
        modalDate.textContent = review.date;
        
        // 이미지 설정
        modalImages.innerHTML = '';
        modalImages.classList.remove('no-image');
        
        // 리뷰 이미지가 있으면 리뷰 이미지 표시
        if (review.images.length > 0) {
            // 리뷰 이미지가 여러 개면 슬라이드쇼
            if (review.images.length > 1) {
                modalImages.classList.add('slideshow');
            }
            
            review.images.forEach((imageUrl, index) => {
                const img = document.createElement('img');
                img.src = imageUrl;
                img.alt = '리뷰 이미지';
                img.className = index === 0 ? 'active' : '';
                img.style.objectFit = window.innerWidth <= 768 ? 'contain' : 'cover';
                modalImages.appendChild(img);
            });
            
            // 리뷰 이미지가 여러 개일 때 슬라이드쇼 시작
            if (review.images.length > 1) {
                let currentImageIndex = 0;
                slideInterval = setInterval(() => {
                    if (!reviewModal || !reviewModal.classList.contains('active')) {
                        clearInterval(slideInterval);
                        return;
                    }
                    
                    const images = modalImages ? modalImages.querySelectorAll('img') : [];
                    if (images.length === 0) {
                        clearInterval(slideInterval);
                        return;
                    }
                    
                    if (images[currentImageIndex]) {
                        images[currentImageIndex].classList.remove('active');
                    }
                    currentImageIndex = (currentImageIndex + 1) % images.length;
                    if (images[currentImageIndex]) {
                        images[currentImageIndex].classList.add('active');
                    }
                }, 3000);
            }
        } 
        // 리뷰 이미지가 없으면 상품 이미지 슬라이드쇼
        else if (review.productImages && review.productImages.length > 0) {
            modalImages.classList.add('slideshow');
            
            review.productImages.forEach((imageUrl, index) => {
                const img = document.createElement('img');
                img.src = imageUrl;
                img.alt = '상품 이미지';
                img.className = index === 0 ? 'active' : '';
                img.style.objectFit = window.innerWidth <= 768 ? 'contain' : 'cover';
                modalImages.appendChild(img);
            });
            
            // 슬라이드쇼 시작 (3초마다)
            let currentImageIndex = 0;
            slideInterval = setInterval(() => {
                if (!reviewModal || !reviewModal.classList.contains('active')) {
                    clearInterval(slideInterval);
                    return;
                }
                
                const images = modalImages ? modalImages.querySelectorAll('img') : [];
                if (images.length === 0) {
                    clearInterval(slideInterval);
                    return;
                }
                
                if (images[currentImageIndex]) {
                    images[currentImageIndex].classList.remove('active');
                }
                currentImageIndex = (currentImageIndex + 1) % images.length;
                if (images[currentImageIndex]) {
                    images[currentImageIndex].classList.add('active');
                }
            }, 3000);
        }
        // 둘 다 없으면 아이콘 표시
        else {
            modalImages.classList.add('no-image');
            modalImages.textContent = '📷';
        }
        
        // 모달 표시
        reviewModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // 스크롤 방지
        
        // 네비게이션 버튼 업데이트
        updateNavButtons();
        
        // 이미지 슬라이더 초기화 (즉시 첫 이미지로)
        if (modalImages) {
            // 애니메이션 없이 즉시 첫 이미지로 이동
            modalImages.style.transition = 'none';
            modalImages.style.transform = 'translateX(0%)';
            // transition 복원을 더 늦게 실행
            setTimeout(() => {
                modalImages.style.transition = '';
            }, 300);
        }
        
        // Chat bot 아이콘 숨기기
        const chatBot = document.querySelector('.floating-chat');
        if (chatBot) {
            chatBot.style.display = 'none';
        }
        
        // 모바일에서 터치 스크롤 방지
        if (window.innerWidth <= 768) {
            document.addEventListener('touchmove', preventScroll, { passive: false });
        }
    }
    
    // 터치 스크롤 방지 함수
    function preventScroll(e) {
        e.preventDefault();
    }
    
    // 모달 닫기
    function closeReviewModal() {
        if (reviewModal) {
            reviewModal.classList.remove('active');
        }
        if (modalImages) {
            modalImages.classList.remove('slideshow');
        }
        document.body.style.overflow = ''; // 스크롤 복원
        
        // 모바일 터치 스크롤 방지 해제
        if (window.innerWidth <= 768) {
            document.removeEventListener('touchmove', preventScroll);
        }
        
        // Chat bot 아이콘 다시 표시
        const chatBot = document.querySelector('.floating-chat');
        if (chatBot) {
            chatBot.style.display = '';
        }
    }
    
    // 모달 이벤트 리스너
    if (modalClose) {
        modalClose.addEventListener('click', closeReviewModal);
    }
    
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeReviewModal);
    }
    
    // 네비게이션 버튼 이벤트 리스너
    if (modalPrev) {
        modalPrev.addEventListener('click', (e) => {
            e.stopPropagation();
            showPrevReview();
        });
    }
    
    if (modalNext) {
        modalNext.addEventListener('click', (e) => {
            e.stopPropagation();
            showNextReview();
        });
    }
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && reviewModal && reviewModal.classList.contains('active')) {
            closeReviewModal();
        }
        
        // 화살표 키로 네비게이션
        if (reviewModal && reviewModal.classList.contains('active')) {
            if (e.key === 'ArrowLeft') {
                showPrevReview();
            } else if (e.key === 'ArrowRight') {
                showNextReview();
            }
        }
    });
});