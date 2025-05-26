// === Theme Toggle ===
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
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    document.querySelector('.theme-icon').innerHTML = '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />';
}

// === Notification ===
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.querySelector('p').textContent = message;
    notification.classList.add('active');
    setTimeout(() => notification.classList.remove('active'), 3000);
}

// === Swipe Cards ===
const cardStack = document.getElementById('cardStack');
let mentors = Array.from(document.querySelectorAll('.mentor-card'));
let lastSwiped = null;

function updateCardStack() {
    mentors.forEach((card, index) => {
        card.style.zIndex = mentors.length - index;
        card.style.transform = index === 0 ? 'none' : `scale(${1 - index * 0.03}) translateY(${index * 8}px)`;
        card.style.pointerEvents = index === 0 ? 'auto' : 'none';
    });
}

function swipeCard(direction) {
    const card = mentors[0];
    if (!card) return;

    const isLike = direction === 'right';
    const stamp = card.querySelector(isLike ? '.swipe-stamp.like' : '.swipe-stamp.nope');
    const xPos = isLike ? 600 : -600;
    const rotation = isLike ? 25 : -25;

    gsap.to(stamp, { opacity: 1, duration: 0.3 });
    gsap.to(card, {
        x: xPos,
        rotate: rotation,
        opacity: 0,
        duration: 0.6,
        ease: 'power2.out',
        onComplete: () => {
            lastSwiped = { card, direction };


            const id = card.getAttribute('data-id');
            const name = card.getAttribute('data-mentor');
            const subject = card.getAttribute('data-subject');
            const profilePic = card.querySelector('img').getAttribute('src');

            if (isLike && id) {
                showMatchModal(id, name, subject);
            } else if (!id) {
                console.error("⚠️ Mentor card missing data-id attribute.");
            }

            card.remove();
            mentors.shift();

            if (isLike) {
                showMatchModal(id, name, subject);
            }
            updateCardStack();
            gsap.set(stamp, { opacity: 0 });
            showNotification(isLike ? 'Mentor combinado!' : 'Mentor rejeitado!');
        }
    });
}


function showMatchModal(id, name, subject) {
    const modal = document.getElementById('matchModal');
    console.log("Setting mentor ID:", id);
    modal.setAttribute('data-mentor-id', id);  // store mentor ID for later
    document.getElementById('matchMentorName').textContent = name;
    document.getElementById('matchMentorSubject').textContent = subject;
    modal.classList.add('active');
}


function closeMatchModal() {
    document.getElementById('matchModal').classList.remove('active');
}



function connectWithMentor() {
    const modal = document.getElementById('matchModal');
    const mentorId = parseInt(modal.getAttribute('data-mentor-id'), 10);
    console.log("Connecting with mentor ID:", mentorId);

    if (!mentorId || isNaN(mentorId)) {
        alert("Erro: mentor não encontrado.");
        return;
    }

 
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

fetch('/start_conversation', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ mentor_id: mentorId })
})

    .then(res => res.json())
    .then(data => {
        console.log("Response from server:", data);
        if (data.status === 'success') {
            window.location.href = `/conversa/${data.conversation_id}`;
        } else {
            alert("Erro ao iniciar conversa: " + data.message);
        }
    })
    .catch((err) => {
        console.error("Fetch error:", err);
        alert("Erro ao comunicar com o servidor.");
    });
}



// === Drag Events for Swipe ===
let isDragging = false;
let startX = 0;
let currentX = 0;

function handleDragStart(e) {
    const card = mentors[0];
    if (!card) return;
    isDragging = true;
    startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
    card.style.transition = 'none';
    e.preventDefault();
}

function handleDragMove(e) {
    if (!isDragging) return;
    const card = mentors[0];
    if (!card) return;
    currentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
    const deltaX = currentX - startX;
    const rotation = deltaX / 8;
    card.style.transform = `translateX(${deltaX}px) rotate(${rotation}deg)`;
    card.style.opacity = 1 - Math.abs(deltaX) / 400;
    card.style.border = deltaX > 0 ? '3px solid #28a745' : '3px solid #dc3545';
    const stamp = card.querySelector(deltaX > 0 ? '.swipe-stamp.like' : '.swipe-stamp.nope');
    gsap.set(stamp, { opacity: Math.abs(deltaX) / 150 });
}

function handleDragEnd() {
    if (!isDragging) return;
    isDragging = false;
    const card = mentors[0];
    if (!card) return;
    card.style.transition = 'transform 0.6s ease, opacity 0.6s ease';
    const deltaX = currentX - startX;
    if (Math.abs(deltaX) > 120) {
        swipeCard(deltaX > 0 ? 'right' : 'left');
    } else {
        gsap.to(card, { x: 0, rotate: 0, opacity: 1, duration: 0.3 });
        card.style.border = 'none';
        gsap.set(card.querySelectorAll('.swipe-stamp'), { opacity: 0 });
    }
}

cardStack.addEventListener('mousedown', handleDragStart);
cardStack.addEventListener('mousemove', handleDragMove);
cardStack.addEventListener('mouseup', handleDragEnd);
cardStack.addEventListener('mouseleave', handleDragEnd);
cardStack.addEventListener('touchstart', handleDragStart);
cardStack.addEventListener('touchmove', handleDragMove);
cardStack.addEventListener('touchend', handleDragEnd);

updateCardStack();
