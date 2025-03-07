
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
