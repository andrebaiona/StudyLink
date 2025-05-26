        // Inicializar Highlight.js
        hljs.highlightAll();

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

        // Animação GSAP para o formulário
        gsap.fromTo('.form-container', 
            { opacity: 0, y: 50 },
            { opacity: 1, y: 0, duration: 1, ease: 'power2.out' }
        );

        // Manipular upload de imagem
        function handleImageUpload(files) {
            const file = files[0];
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) {
                showNotification('Imagem demasiado grande! Máximo 5MB.');
                return;
            }
            showNotification('Imagem selecionada com sucesso!');
        }

        // Criar tópico
        function createTopic() {
            const title = document.getElementById('topicTitle').value.trim();
            const subject = document.getElementById('topicSubject').value;
            const content = document.getElementById('topicContent').value.trim();
            const image = document.getElementById('topicImage').files[0];

            if (!title || !subject || !content) {
                showNotification('Por favor, preencha todos os campos obrigatórios.');
                return;
            }

            // Simulação de envio de dados
            showNotification('Tópico criado com sucesso!');
            setTimeout(() => {
                location.href = '/comunidade.html';
            }, 1000);

            // Aqui você pode adicionar a lógica para enviar os dados ao servidor
            // Exemplo: 
            /*
            const formData = new FormData();
            formData.append('title', title);
            formData.append('subject', subject);
            formData.append('content', content);
            if (image) formData.append('image', image);

            fetch('/api/create-topic', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                showNotification('Tópico criado com sucesso!');
                setTimeout(() => {
                    location.href = '/comunidade.html';
                }, 1000);
            })
            .catch(error => {
                showNotification('Erro ao criar tópico. Tente novamente.');
            });
            */
        }