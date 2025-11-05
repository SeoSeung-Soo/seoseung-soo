document.addEventListener('DOMContentLoaded', function() {
    const paymentSuccess = document.body.dataset.paymentSuccess === 'true';
    
    if (paymentSuccess && typeof toast !== 'undefined') {
        toast.success('주문이 완료되었습니다!', '주문 완료', 3000);
    }
});
