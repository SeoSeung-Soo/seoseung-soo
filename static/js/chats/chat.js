document.addEventListener('DOMContentLoaded', function() {
    const chatButton = document.getElementById('chatButton');
    const chatWindow = document.getElementById('chatWindow');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const newsFeedPrev = document.getElementById('newsFeedPrev');
    const newsFeedNext = document.getElementById('newsFeedNext');
    const newsFeedContainer = document.querySelector('.news-feed-container');
    const faqBtn = document.getElementById('faqBtn');
    
    const inquireBtn = document.getElementById('inquireBtn');
    const inquireBackBtn = document.getElementById('inquireBackBtn');
    const newsFeedSlide = document.getElementById('newsFeedSlide');
    const inquireFormSlide = document.getElementById('inquireFormSlide');
    const chatHeaderLogo = document.getElementById('chatHeaderLogo');
    const chatHeaderBack = document.getElementById('chatHeaderBack');
    
    function openChatWindow() {
        if (chatWindow) {
            chatWindow.classList.add('active');
        }
    }
    
    function closeChatWindow() {
        if (chatWindow) {
            chatWindow.classList.remove('active');
        }
        if (newsFeedSlide && inquireFormSlide) {
            newsFeedSlide.classList.add('active');
            inquireFormSlide.classList.remove('active');
        }
        if (chatHeaderLogo && chatHeaderBack) {
            chatHeaderLogo.classList.add('active');
            chatHeaderBack.classList.remove('active');
        }
    }
    
    function toggleChatWindow() {
        if (chatWindow && chatWindow.classList.contains('active')) {
            closeChatWindow();
        } else {
            openChatWindow();
        }
    }
    
    if (chatButton) {
        chatButton.addEventListener('click', toggleChatWindow);
    }
    
    if (chatCloseBtn) {
        chatCloseBtn.addEventListener('click', closeChatWindow);
    }
    
    if (newsFeedPrev && newsFeedContainer) {
        newsFeedPrev.addEventListener('click', function() {
            newsFeedContainer.scrollBy({
                left: -180,
                behavior: 'smooth'
            });
        });
    }
    
    if (newsFeedNext && newsFeedContainer) {
        newsFeedNext.addEventListener('click', function() {
            newsFeedContainer.scrollBy({
                left: 180,
                behavior: 'smooth'
            });
        });
    }
    
    if (faqBtn) {
        faqBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('자주 묻는 질문 기능은 준비중입니다.');
        });
    }
    
    if (inquireBtn && newsFeedSlide && inquireFormSlide && chatHeaderLogo && chatHeaderBack) {
        inquireBtn.addEventListener('click', function() {
            newsFeedSlide.classList.remove('active');
            inquireFormSlide.classList.add('active');
            chatHeaderLogo.classList.remove('active');
            chatHeaderBack.classList.add('active');
        });
    }
    
    if (inquireBackBtn && newsFeedSlide && inquireFormSlide && chatHeaderLogo && chatHeaderBack) {
        inquireBackBtn.addEventListener('click', function() {
            newsFeedSlide.classList.add('active');
            inquireFormSlide.classList.remove('active');
            chatHeaderLogo.classList.add('active');
            chatHeaderBack.classList.remove('active');
        });
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatWindow && chatWindow.classList.contains('active')) {
            closeChatWindow();
        }
    });
    
    const chatInquireForm = document.getElementById('chatInquireForm');
    if (chatInquireForm) {
        chatInquireForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(chatInquireForm);
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const submitBtn = chatInquireForm.querySelector('.chat-submit-btn');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = '전송 중...';
            
            fetch(chatInquireForm.action, {
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
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                
                if (data.success) {
                    if (typeof toast !== 'undefined') {
                        toast.success('문의가 성공적으로 전송되었습니다.', '문의하기');
                    } else {
                        alert('문의가 성공적으로 전송되었습니다.');
                    }
                    chatInquireForm.reset();
                    if (newsFeedSlide && inquireFormSlide) {
                        newsFeedSlide.classList.add('active');
                        inquireFormSlide.classList.remove('active');
                    }
                    if (chatHeaderLogo && chatHeaderBack) {
                        chatHeaderLogo.classList.add('active');
                        chatHeaderBack.classList.remove('active');
                    }
                } else {
                    if (typeof toast !== 'undefined') {
                        toast.error(data.message, '오류');
                    } else {
                        alert(data.message);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
                if (typeof toast !== 'undefined') {
                    toast.error('문의 전송 중 오류가 발생했습니다.', '오류');
                } else {
                    alert('문의 전송 중 오류가 발생했습니다.');
                }
            });
        });
    }
});

