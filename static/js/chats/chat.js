document.addEventListener('DOMContentLoaded', function() {
    const chatButton = document.getElementById('chatButton');
    const chatWindow = document.getElementById('chatWindow');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const newsFeedPrev = document.getElementById('newsFeedPrev');
    const newsFeedNext = document.getElementById('newsFeedNext');
    const newsFeedContainer = document.querySelector('.news-feed-container');
    
    function openChatWindow() {
        if (chatWindow) {
            chatWindow.classList.add('active');
        }
    }
    
    function closeChatWindow() {
        if (chatWindow) {
            chatWindow.classList.remove('active');
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
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && chatWindow && chatWindow.classList.contains('active')) {
            closeChatWindow();
        }
    });
});

