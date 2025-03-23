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

