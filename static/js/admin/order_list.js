document.addEventListener('DOMContentLoaded', function() {
    const orderRows = document.querySelectorAll('.order-row-clickable');
    
    orderRows.forEach(function(row) {
        row.addEventListener('click', function(e) {
            if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
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
