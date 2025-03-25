function toggleAccountMenu() {
    const menu = document.getElementById('accountMenu');
    if (menu) {
        // Abre ou fecha o menu ao clicar no botão
        menu.classList.toggle('show');
    }
}

// Detectar quando o mouse sai da área do menu ou do botão
const accountBtn = document.querySelector('.account-btn');
const accountMenu = document.getElementById('accountMenu');

// Fechar o menu quando o mouse sair de qualquer área
document.addEventListener('mousemove', (event) => {
    const isMouseOutsideMenu = !accountMenu.contains(event.target) && !accountBtn.contains(event.target);
    if (isMouseOutsideMenu && accountMenu.classList.contains('show')) {
        accountMenu.classList.remove('show');
    }
});
