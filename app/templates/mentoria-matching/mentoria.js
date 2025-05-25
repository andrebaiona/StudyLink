let mentors = [
    { name: "João Silva", img: "assets/images/joao.jpg", desc: "Especialista em Web Development" },
    { name: "Maria Souza", img: "assets/images/maria.jpg", desc: "Mentora de UX/UI Design" },
    { name: "Carlos Lima", img: "assets/images/carlos.jpg", desc: "Engenheiro de Dados" }
];

let currentIndex = 0;

function loadMentor() {
    if (currentIndex < mentors.length) {
        document.getElementById("mentor-name").innerText = mentors[currentIndex].name;
        document.getElementById("mentor-desc").innerText = mentors[currentIndex].desc;
        document.getElementById("mentor-img").src = mentors[currentIndex].img;
    } else {
        document.querySelector(".card").innerHTML = "<h5>Sem mais mentores!</h5>";
    }
}

function acceptMentor() {
    alert(`Você aceitou ${mentors[currentIndex].name}!`);
    nextMentor();
}

function rejectMentor() {
    nextMentor();
}

function nextMentor() {
    currentIndex++;
    loadMentor();
}

window.onload = loadMentor;
