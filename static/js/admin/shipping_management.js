document.addEventListener('DOMContentLoaded', function() {
    const shippingRows = document.querySelectorAll('.shipping-row-clickable');
    
    shippingRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            if (e.target.tagName !== 'SELECT' && e.target.tagName !== 'OPTION' && e.target.tagName !== 'FORM' && !e.target.closest('form')) {
                const isExpanded = this.classList.contains('expanded');
                
                if (isExpanded) {
                    this.classList.remove('expanded');
                } else {
                    this.classList.add('expanded');
                }
            }
        });
    });
});
