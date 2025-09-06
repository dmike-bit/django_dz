// Основные скрипты для библиотеки
document.addEventListener('DOMContentLoaded', function() {
    console.log('Библиотека загружена!');
    
    // Плавная прокрутка для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Подсветка активной ссылки в навигации
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-menu a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = '#3498db';
            link.style.fontWeight = 'bold';
        }
    });
});