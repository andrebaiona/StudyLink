        // Alternar sidebar
        function toggleSidebar() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('active');
        }

        // Efeito de rolagem na barra de navegação
        window.addEventListener('scroll', () => {
            const header = document.querySelector('header');
            header.classList.toggle('scrolled', window.scrollY > 50);
        });

        // Funções de modal
        function openScheduleModal() {
            document.getElementById('scheduleModal').classList.add('active');
        }

        function openMessageModal(mentorName) {
            const modal = document.getElementById('messageModal');
            modal.querySelector('#mentorName').value = mentorName;
            modal.classList.add('active');
        }

        function openGoalModal() {
            document.getElementById('goalModal').classList.add('active');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.remove('active');
        }

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

        // Animações GSAP
        gsap.registerPlugin(ScrollTrigger);

        document.querySelectorAll('section').forEach(section => {
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

        // Navegação da barra lateral
        document.querySelectorAll('.sidebar-nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                const targetId = link.getAttribute('href').substring(1);
                document.getElementById(targetId).scrollIntoView({ behavior: 'smooth' });
                if (window.innerWidth < 768) {
                    toggleSidebar();
                }
            });
        });

        // Formulários
        document.querySelector('#scheduleModal form').addEventListener('submit', (e) => {
            e.preventDefault();
            closeModal('scheduleModal');
            showNotification('Sessão agendada com sucesso!');
        });

        document.querySelector('#messageModal form').addEventListener('submit', (e) => {
            e.preventDefault();
            closeModal('messageModal');
            showNotification('Mensagem enviada com sucesso!');
        });

        document.querySelector('#goalModal form').addEventListener('submit', (e) => {
            e.preventDefault();
            closeModal('goalModal');
            showNotification('Meta adicionada com sucesso!');
        });

        // Gráficos
        const studyTimeCtx = document.getElementById('studyTimeChart').getContext('2d');
        new Chart(studyTimeCtx, {
            type: 'line',
            data: {
                labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                datasets: [{
                    label: 'Horas de Estudo',
                    data: [2, 3, 1.5, 4, 2.5, 3, 0],
                    borderColor: 'var(--accent-primary)',
                    backgroundColor: 'rgba(160, 82, 45, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Horas'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        const activityCtx = document.getElementById('activityChart').getContext('2d');
        new Chart(activityCtx, {
            type: 'bar',
            data: {
                labels: ['Posts', 'Recursos', 'Sessões', 'Metas'],
                datasets: [{
                    label: 'Atividade',
                    data: [5, 10, 8, 3],
                    backgroundColor: 'var(--accent-primary)',
                    borderColor: 'var(--accent-secondary)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantidade'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Inicializar sidebar para telas pequenas
        if (window.innerWidth < 768) {
            document.querySelector('.sidebar').classList.add('hidden');
        }