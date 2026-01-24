function showExchangeRefundModal(orderId, orderNumber, orderAmount) {
    document.getElementById('exchangeRefundOrderId').textContent = orderNumber;
    document.getElementById('exchangeRefundOrderAmount').textContent = orderAmount.toLocaleString();
    document.getElementById('exchangeRefundForm').action = `/orders/exchange-refund/${orderId}/`;
    document.getElementById('exchangeRefundModal').style.display = 'block';
}

function closeExchangeRefundModal() {
    document.getElementById('exchangeRefundModal').style.display = 'none';
    document.getElementById('exchangeRefundType').value = '';
    document.getElementById('exchangeRefundReason').value = '';
}

window.onclick = function(event) {
    const modal = document.getElementById('exchangeRefundModal');
    if (event.target === modal) {
        closeExchangeRefundModal();
    }
}
