// Animações GSAP
        gsap.fromTo('.post-card', 
            { opacity: 0, y: 30 },
            { opacity: 1, y: 0, duration: 0.8, stagger: 0.2, ease: 'power2.out', scrollTrigger: { trigger: '.posts-grid', start: 'top 80%' } }
        );

        // Procurar posts
        function searchPosts(query) {
            const posts = document.querySelectorAll('.post-card');
            posts.forEach(post => {
                const title = post.querySelector('h3').textContent.toLowerCase();
                const content = post.querySelector('.post-content').textContent.toLowerCase();
                post.style.display = (title.includes(query.toLowerCase()) || content.includes(query.toLowerCase())) ? 'block' : 'none';
            });
        }

        // Filtrar posts por disciplina
        function filterPosts(subject) {
            const posts = document.querySelectorAll('.post-card');
            posts.forEach(post => {
                const postSubject = post.querySelector('.post-meta span:last-child').textContent;
                post.style.display = (subject === 'all' || postSubject === subject) ? 'block' : 'none';
            });
        }

        // Alternar like
        function toggleLike(button) {
            button.classList.toggle('liked');
            const likeCount = button.querySelector('.like-count');
            let count = parseInt(likeCount.textContent);
            likeCount.textContent = button.classList.contains('liked') ? count + 1 : count - 1;
            showNotification(button.classList.contains('liked') ? 'Gostou do post!' : 'Removido o gosto.');
        }

        // Abrir modal de post
        function openPostModal(title, author, date, subject, content, image) {
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalAuthor').textContent = author;
            document.getElementById('modalDate').textContent = date;
            document.getElementById('modalSubject').textContent = subject;
            document.getElementById('modalContent').innerHTML = content;
            const modalImage = document.getElementById('modalImage');
            if (image) {
                modalImage.src = image;
                modalImage.style.display = 'block';
            } else {
                modalImage.style.display = 'none';
            }
            document.getElementById('postModal').classList.add('active');
            hljs.highlightAll();
        }

        // Fechar modal de post
        function closePostModal() {
            const modal = document.getElementById('postModal');
            modal.style.display = 'none';
        }

        // Navegar para criar post
        function navigateToCreatePost() {
            showNotification('A redirecionar para criar um novo post...');
            setTimeout(() => {
                location.href = '/formulario.html';
            }, 1000);
        }

        // Fechar modal ao clicar fora
        document.getElementById('postModal').addEventListener('click', (e) => {
            if (e.target === document.getElementById('postModal')) {
                closePostModal();
            }
        });