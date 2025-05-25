// Inicializar Highlight.js
hljs.highlightAll();

// Alternar tema
function toggleTheme() {
    const body = document.body;
    const toggleIcon = document.querySelector('.theme-icon');
    body.classList.toggle('dark-mode');
    toggleIcon.innerHTML = body.classList.contains('dark-mode')
        ? '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />'
        : '<path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />';
    localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
    showNotification('Tema alterado!');
}

// Verificar tema guardado
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    document.querySelector('.theme-icon').innerHTML = '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />';
}

// Alternar menu
function toggleMenu() {
    const nav = document.querySelector('nav');
    const btn = document.querySelector('.menu-btn');
    nav.classList.toggle('show');
    btn.classList.toggle('active');
}

// Efeito de rolagem na barra de navegação
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    header.classList.toggle('scrolled', window.scrollY > 50);
});

// Função de logout
function logout() {
    showNotification('Sessão terminada com sucesso!');
    setTimeout(() => {
        location.href = '/login_page';
    }, 1000);
}

// Função de notificação
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.querySelector('p').textContent = message;
    notification.classList.add('active');
    setTimeout(() => {
        notification.classList.remove('active');
    }, 3000);
}