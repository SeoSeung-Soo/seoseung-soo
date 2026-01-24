function showApprovalModal(orderId, orderNumber) {
    document.getElementById('approvalOrderNumber').textContent = orderNumber;
    document.getElementById('approvalForm').action = `/orders/admin/exchange-refund/${orderId}/process/`;
    document.getElementById('approvalModal').style.display = 'block';
}

function showRejectModal(orderId, orderNumber) {
    document.getElementById('rejectOrderNumber').textContent = orderNumber;
    document.getElementById('rejectForm').action = `/orders/admin/exchange-refund/${orderId}/process/`;
    document.getElementById('rejectModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    if (modalId === 'approvalModal') {
        document.getElementById('approvalAdminNote').value = '';
    } else if (modalId === 'rejectModal') {
        document.getElementById('rejectAdminNote').value = '';
    }
}

window.onclick = function(event) {
    const approvalModal = document.getElementById('approvalModal');
    const rejectModal = document.getElementById('rejectModal');
    if (event.target === approvalModal) {
        closeModal('approvalModal');
    }
    if (event.target === rejectModal) {
        closeModal('rejectModal');
    }
}
