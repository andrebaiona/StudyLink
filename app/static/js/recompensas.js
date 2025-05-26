        window.addEventListener('scroll', () => {
            const header = document.querySelector('header');
            header.classList.toggle('scrolled', window.scrollY > 50);
        });

        function showNotification(message) {
            const notification = document.getElementById('notification');
            notification.querySelector('p').textContent = message;
            notification.classList.add('active');
            setTimeout(() => {
                notification.classList.remove('active');
            }, 3000);
        }

        // Rewards Functionality (Demo)
        function redeemReward(rewardId, points) {
            // Simulate reward redemption
            showNotification(`Recompensa resgatada! (-${points} pontos)`);
            // In a real app, this would update points and history
        }

        // GSAP Animations
        gsap.fromTo('.rewards-container', 
            { opacity: 0, y: 50 },
            { opacity: 1, y: 0, duration: 1, ease: 'power2.out' }
        );

        gsap.fromTo('.reward-card', 
            { opacity: 0, x: -30 },
            { opacity: 1, x: 0, duration: 0.8, stagger: 0.2, ease: 'power2.out' }
        );