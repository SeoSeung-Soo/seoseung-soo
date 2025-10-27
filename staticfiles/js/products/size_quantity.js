let quantity = 1;
let selectedSize = null;
let maxStock = 99;

function increaseQuantity() {
    quantity = Math.min(quantity + 1, maxStock);
    updateQuantityDisplay();
}

function decreaseQuantity() {
    quantity = Math.max(quantity - 1, 1);
    updateQuantityDisplay();
}

function updateQuantityDisplay() {
    document.getElementById('quantityDisplay').textContent = quantity;
}

function setMaxStock(stock) {
    maxStock = Math.max(parseInt(stock), 1);
    if (quantity > maxStock) {
        quantity = maxStock;
        updateQuantityDisplay();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const sizeQuantitySection = document.querySelector('.size-quantity-section');
    if (sizeQuantitySection) {
        const productStock = parseInt(sizeQuantitySection.getAttribute('data-product-stock'));
        if (!isNaN(productStock)) {
            setMaxStock(productStock);
        }
    }
    
    const sizeButtons = document.querySelectorAll('.size-btn');
    
    sizeButtons.forEach(button => {
        button.addEventListener('click', function() {
            sizeButtons.forEach(btn => btn.classList.remove('selected'));
            
            this.classList.add('selected');
            selectedSize = this.getAttribute('data-size');
        });
    });
    
    updateQuantityDisplay();
});