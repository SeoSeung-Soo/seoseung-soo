document.addEventListener('DOMContentLoaded', function() {
    const colorPicker = document.querySelector('.color-picker');
    const colorPreview = document.getElementById('colorPreview');
    
    if (colorPicker && colorPreview) {
        updateColorPreview();
        
        colorPicker.addEventListener('input', updateColorPreview);
        colorPicker.addEventListener('change', updateColorPreview);
        
        function updateColorPreview() {
            const selectedColor = colorPicker.value || '#000000';
            colorPreview.style.backgroundColor = selectedColor;
        }
    }
});

