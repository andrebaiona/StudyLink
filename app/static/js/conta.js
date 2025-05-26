$(document).ready(function() {
    $('#mentor_units, #mentee_units').select2({
        placeholder: "Selecione unidades curriculares",
        width: '100%'
    });
});

// GSAP Animation
gsap.fromTo('.account-container', 
    { opacity: 0, y: 50 },
    { opacity: 1, y: 0, duration: 1, ease: 'power2.out' }
);

// Preview Profile Image
function previewProfileImage() {
    const input = document.getElementById('profile_pic');
    const preview = document.getElementById('profilePreview');
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            showNotification('Imagem de perfil selecionada!');
        };
        reader.readAsDataURL(file);
    }
}

// Update Course Year Options
function updateYearOptions() {
    const courseType = document.getElementById('course_type').value;
    const classYear = document.getElementById('class_year');
    classYear.innerHTML = '';

    let maxYears = 3;
    if (courseType === 'Mestrado') {
        maxYears = 2;
    } else if (courseType === 'Pós-Graduação') {
        maxYears = 1;
    }

    for (let i = 1; i <= maxYears; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `${i}º`;
        classYear.appendChild(option);
    }
}

// Initialize Course Year Options
document.addEventListener('DOMContentLoaded', () => {
    updateYearOptions();
});

function toggleAccountMenu() {
            const menu = document.getElementById('accountMenu');
            menu.classList.toggle('show');
        }

        function previewProfileImage() {
            const file = document.getElementById('profile_pic').files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    document.getElementById('profilePreview').src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        }

        
function updateYearOptions() {
    const courseType = document.getElementById('course_type').value;
    const yearSelect = document.getElementById('class_year');
    
    let years = [];
    if (courseType === "Licenciatura") {
        years = ["1", "2", "3"];
    } else if (courseType === "Mestrado") {
        years = ["1", "2"];
    } else if (courseType === "Pós-Graduação") {
        years = ["1"];
    }

    const selectedYear = yearSelect.value; 

    yearSelect.innerHTML = "";
    years.forEach(year => {
        let option = document.createElement("option");
        option.value = year;
        option.textContent = year + "º";
        if (year === selectedYear) {
            option.selected = true;          }
        yearSelect.appendChild(option);
    });
}

document.addEventListener("DOMContentLoaded", updateYearOptions);

