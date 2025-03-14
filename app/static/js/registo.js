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


