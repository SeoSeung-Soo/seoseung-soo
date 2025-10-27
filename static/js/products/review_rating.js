document.addEventListener('DOMContentLoaded', function() {
    // 평점에 따른 별점 색상 설정
    const starRatings = document.querySelectorAll('.star-rating');
    starRatings.forEach(function(starRating) {
        const rating = parseFloat(starRating.dataset.rating);
        const starsFill = starRating.querySelector('.stars-fill');
        
        if (rating > 0) {
            // 평점을 퍼센트로 변환 (5점 만점 기준)
            const percentage = (rating / 5) * 100;
            starsFill.style.width = percentage + '%';
        } else {
            starsFill.style.width = '0%';
        }
    });
});