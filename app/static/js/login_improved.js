
document.addEventListener("DOMContentLoaded", function () {
    let flashMessage = document.querySelector(".flash-message.success");
    if (flashMessage) {
      
      flashMessage.style.display = "block";
      
  
      setTimeout(() => {
        window.location.href = "/conta";
      }, 3000);
    }
});


document.addEventListener("DOMContentLoaded", function () {
    // Verifica se há uma flash message de sucesso
    let flashMessage = document.querySelector(".flash-message.success");
    if (flashMessage) {
        // Garante que a flash message esteja visível
        flashMessage.style.display = "block";
        
        // Se existir um container de carregamento, remove a classe "hidden"
        let loadingContainer = document.getElementById("loading-container");
        if (loadingContainer) {
            setTimeout(() => {
                loadingContainer.classList.remove("hidden");
            }, 500);
        }
        
        // Após 5 segundos, redireciona para /conta
        setTimeout(() => {
            window.location.href = "/conta";
        }, 5000);
    }
    
    // Fade out para todas as flash messages após 3 segundos
    setTimeout(function () {
        let flashMessages = document.querySelectorAll(".flash-message");
        flashMessages.forEach(msg => {
            msg.style.transition = "opacity 0.5s";
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500);
        });
    }, 3000);
});


function togglePassword(fieldId, iconElement) {
  const passwordField = document.getElementById(fieldId);
  const eyeIcon = iconElement.querySelector('i');

  if (passwordField.type === 'password') {
    passwordField.type = 'text';
    eyeIcon.classList.remove('fa-eye');
    eyeIcon.classList.add('fa-eye-slash');
  } else {
    passwordField.type = 'password';
    eyeIcon.classList.remove('fa-eye-slash');
    eyeIcon.classList.add('fa-eye');
  }
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