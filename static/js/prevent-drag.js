// 드래그 방지 스크립트
document.addEventListener('DOMContentLoaded', function() {
    // 모든 이미지와 링크에 드래그 방지 속성 추가
    function preventDrag(element) {
        element.setAttribute('draggable', 'false');
        element.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });
        element.addEventListener('drag', function(e) {
            e.preventDefault();
            return false;
        });
        element.addEventListener('dragend', function(e) {
            e.preventDefault();
            return false;
        });
    }
    
    // 페이지 로드 시 모든 이미지와 링크 처리
    const images = document.querySelectorAll('img');
    const links = document.querySelectorAll('a');
    
    images.forEach(preventDrag);
    links.forEach(preventDrag);
    
    // 동적으로 추가되는 요소들도 처리
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    // 직접 추가된 이미지나 링크
                    if (node.tagName === 'IMG' || node.tagName === 'A') {
                        preventDrag(node);
                    }
                    
                    // 자식 요소들도 확인
                    const childImages = node.querySelectorAll('img');
                    const childLinks = node.querySelectorAll('a');
                    
                    childImages.forEach(preventDrag);
                    childLinks.forEach(preventDrag);
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // 전역 드래그 이벤트 차단
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    });
    
    document.addEventListener('drag', function(e) {
        e.preventDefault();
        return false;
    });
    
    document.addEventListener('dragend', function(e) {
        e.preventDefault();
        return false;
    });
    
    // 컨텍스트 메뉴도 차단 (우클릭 메뉴)
    document.addEventListener('contextmenu', function(e) {
        if (e.target.tagName === 'IMG' || e.target.tagName === 'A') {
            e.preventDefault();
            return false;
        }
    });
});
