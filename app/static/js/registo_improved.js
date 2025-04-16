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

// Verificar tema guardado ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        document.querySelector('.theme-icon').innerHTML = '<path d="M12 3a9 9 0 009 9 9 9 0 00-9 9 9 9 0 00-9-9 9 9 0 009-9z" />';
    }
});

/* Javascript para Medidor de força da Password */
document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const strengthBar = document.querySelector(".password-strength-bar");

    if (passwordInput && strengthBar) {
        passwordInput.addEventListener("input", function () {
            const strength = checkPasswordStrength(passwordInput.value);
            updateStrengthBar(strength);
        });
    }

    function checkPasswordStrength(password) {
        let score = 0;
        if (password.length >= 12) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[a-z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[@$!%*?&]/.test(password)) score++; 
        return score;
    }

    
     
    function updateStrengthBar(score) {
        const colors = ["#e74c3c", "#f1c40f", "#2ecc71", "#3498db", "#8e44ad"];
        const widths = ["20%", "40%", "60%", "80%", "100%"];

        const strengthBar = document.querySelector(".password-strength-bar");

        if (strengthBar) {
            if (score === 0) {
                strengthBar.style.display = "none"; 
            } else {
                strengthBar.style.display = "block"; 
                let index = Math.min(score - 1, widths.length - 1);
                strengthBar.style.width = widths[index];
                strengthBar.style.backgroundColor = colors[index];
            }
        }
}
});


//registo

document.addEventListener("DOMContentLoaded", function () {
    let flashMessage = document.querySelector(".flash-message.success"); 
    if (flashMessage) {
        setTimeout(function () {
            window.location.href = "/login_page"; 
        }, 3000); 
    }
});

document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let flashMessages = document.querySelectorAll(".flash-message");
        flashMessages.forEach(msg => {
            msg.style.transition = "opacity 0.5s";
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500);
        });
    }, 3000); // 3 seconds before fade out
});


document.addEventListener("DOMContentLoaded", function () {
    let flashMessage = document.querySelector(".flash-message.success");
    let loadingContainer = document.getElementById("loading-container");

    if (flashMessage) {
      flashMessage.style.display = "block";
      
      setTimeout(() => {
        loadingContainer.classList.remove("hidden"); 
      }, 500); 

      setTimeout(() => {
        window.location.href = "/conta"; 
      }, 5000); 
    }
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


