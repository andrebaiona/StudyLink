// Função para alternar o tema
function toggleTheme() {
    const body = document.body;
    const toggleIcon = document.querySelector('.theme-icon');
    body.classList.toggle('dark-mode');
    toggleIcon.innerHTML = body.classList.contains('dark-mode')
        ? '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />'
        : '<path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />';
    localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
}

// Verificar tema guardado
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.theme-icon').innerHTML = '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />';
    }
});

// Função para alternar menu mobile
function toggleMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
    if (navLinks.classList.contains('active')) {
        document.querySelector('.dropdown-menu').classList.remove('active');
    }
}

// Função para alternar dropdown
function toggleDropdown() {
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownMenu.classList.toggle('active');
}

// Fechar dropdown ao clicar fora
document.addEventListener('click', (e) => {
    const dropdown = document.querySelector('.dropdown');
    if (!dropdown.contains(e.target)) {
        document.querySelector('.dropdown-menu').classList.remove('active');
    }
});

// Carregar posts
document.addEventListener('DOMContentLoaded', () => {
    const postsContainer = document.getElementById('posts-container');

    // Mock de posts (substituir por chamada ao backend)
    const mockPosts = [
        {
            title: 'Teste de Matemática - 10º Ano',
            author: 'Ana Silva',
            date: '2025-04-14',
            content: 'Partilho um teste de funções com questões sobre derivadas e gráficos.',
            file: 'teste_matematica.pdf'
        },
        {
            title: 'Exercícios de Física - Mecânica',
            author: 'João Pereira',
            date: '2025-04-13',
            content: 'Lista de exercícios resolvidos sobre movimento retilíneo uniforme.',
            file: null
        },
        {
            title: 'Resumo de Literatura - Camões',
            author: 'Maria Costa',
            date: '2025-04-12',
            content: 'Resumo detalhado sobre Os Lusíadas para preparação do exame.',
            file: 'resumo_literatura.docx'
        }
    ];

    // Função para renderizar posts
    function renderPosts(posts) {
        postsContainer.innerHTML = '';
        if (posts.length === 0) {
            postsContainer.innerHTML = '<p class="no-posts">Ainda não há posts na comunidade.</p>';
            return;
        }
        posts.forEach(post => {
            const postElement = document.createElement('article');
            postElement.classList.add('post');
            postElement.innerHTML = `
                <h3>${post.title}</h3>
                <div class="post-meta">Por ${post.author} em ${post.date}</div>
                <div class="post-content">${post.content}</div>
                ${post.file ? `<a href="/static/uploads/${post.file}" class="post-file" target="_blank">Ver Ficheiro</a>` : ''}
            `;
            postsContainer.appendChild(postElement);
        });
    }

    // Carregar posts iniciais
    renderPosts(mockPosts);
});