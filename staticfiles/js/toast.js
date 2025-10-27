class Toast {
    constructor() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            console.error('Toast container not found');
            return;
        }
    }

    createToast(message, type, title) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        toast.innerHTML = `
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">✕</button>
        `;

        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.hide(toast);
        });

        return toast;
    }

    show(message, type = 'success', title = null, duration = 2000) {
        const toast = this.createToast(message, type, title);
        this.container.appendChild(toast);

        const isMobile = window.innerWidth <= 768;
        const actualDuration = isMobile ? duration + 1000 : duration;

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            this.hide(toast);
        }, actualDuration);

        return toast;
    }

    hide(toast) {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        }, { once: true });
    }

    success(message, title = '성공', duration) {
        this.show(message, 'success', title, duration);
    }

    error(message, title = '오류', duration) {
        this.show(message, 'error', title, duration);
    }

    warning(message, title = '경고', duration) {
        this.show(message, 'warning', title, duration);
    }

    info(message, title = '정보', duration) {
        this.show(message, 'info', title, duration);
    }
}

const toast = new Toast();

