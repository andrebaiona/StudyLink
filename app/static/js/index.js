        // Função para alternar o menu
        function toggleMenu() {
            const nav = document.querySelector('nav');
            const btn = document.querySelector('.menu-btn');
            nav.classList.toggle('show');
            btn.classList.toggle('active');
        }

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
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark-mode');
            document.querySelector('.theme-icon').innerHTML = '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />';
        }

        // Efeito de rolagem na barra de navegação
        window.addEventListener('scroll', () => {
            const header = document.querySelector('header');
            header.classList.toggle('scrolled', window.scrollY > 50);
        });

        // Animações GSAP
        gsap.registerPlugin(ScrollTrigger);

        // Animar secções ao entrar na vista
        document.querySelectorAll('main section').forEach(section => {
            gsap.fromTo(section, 
                { opacity: 0, y: 50 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 1,
                    ease: 'power2.out',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top 80%',
                        end: 'bottom 20%',
                        toggleActions: 'play none none reverse'
                    }
                }
            );
        });

        // Efeito de inclinação nos cartões
        document.querySelectorAll('.tilt').forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const tiltX = (y - centerY) / 10;
                const tiltY = -(x - centerX) / 10;
                card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
            });
        });

        // Animação de contadores
        document.querySelectorAll('.counter').forEach(counter => {
            const updateCounter = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText;
                const increment = target / 200;
                if (count < target) {
                    counter.innerText = Math.ceil(count + increment);
                    setTimeout(updateCounter, 20);
                } else {
                    counter.innerText = target;
                }
            };
            const observer = new IntersectionObserver(([entry]) => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.disconnect();
                }
            }, { threshold: 0.5 });
            observer.observe(counter);
        });

        // Carrossel de testemunhos
        const carousel = document.querySelector('.testimonial-grid');
        const cards = document.querySelectorAll('.testimonial-card');
        let currentIndex = 0;

        function updateCarousel() {
            carousel.style.transform = `translateX(-${currentIndex * 33.333}%)`;
        }

        function nextTestimonial() {
            currentIndex = (currentIndex + 1) % cards.length;
            updateCarousel();
        }

        function prevTestimonial() {
            currentIndex = (currentIndex - 1 + cards.length) % cards.length;
            updateCarousel();
        }

        setInterval(nextTestimonial, 6000);

        // Botão voltar ao topo
        const backToTop = document.querySelector('.back-to-top');
        window.addEventListener('scroll', () => {
            backToTop.classList.toggle('visible', window.scrollY > 300);
        });

        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        // Funções do modal
        function openModal() {
            document.getElementById('signupModal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('signupModal').classList.remove('active');
        }

        // Estado ativo dos links de navegação
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                const targetId = link.getAttribute('href').substring(1);
                document.getElementById(targetId).scrollIntoView({ behavior: 'smooth' });
            });
        });

        // Carregamento lento de imagens
        document.querySelectorAll('img.lazy').forEach(img => {
            const observer = new IntersectionObserver(([entry]) => {
                if (entry.isIntersecting) {
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    observer.disconnect();
                }
            });
            observer.observe(img);
        });