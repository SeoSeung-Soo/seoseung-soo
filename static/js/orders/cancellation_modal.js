function showCancellationModal(orderId, orderNumber, orderAmount) {
    document.getElementById('cancellationOrderId').textContent = orderNumber;
    document.getElementById('cancellationOrderAmount').textContent = orderAmount.toLocaleString();
    document.getElementById('cancellationForm').action = `/orders/cancel/${orderId}/`;
    document.getElementById('cancellationModal').style.display = 'block';
}

function closeCancellationModal() {
    document.getElementById('cancellationModal').style.display = 'none';
    document.getElementById('cancellationReason').value = '';
}

window.onclick = function(event) {
    const modal = document.getElementById('cancellationModal');
    if (event.target === modal) {
        closeCancellationModal();
    }
}
