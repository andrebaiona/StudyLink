// GSAP Animations
gsap.fromTo('.resource-container', 
    { opacity: 0, y: 50 },
    { opacity: 1, y: 0, duration: 1, ease: 'power2.out' }
);

gsap.fromTo('.resource-card', 
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.8, stagger: 0.2, ease: 'power2.out' }
);

// Search Resources
function searchResources(query) {
    const resources = document.querySelectorAll('.resource-card');
    resources.forEach(resource => {
        const title = resource.querySelector('h3').textContent.toLowerCase();
        const description = resource.querySelector('p').textContent.toLowerCase();
        resource.style.display = (title.includes(query.toLowerCase()) || description.includes(query.toLowerCase())) ? 'block' : 'none';
    });
}

// Filter Resources
function filterResources(type) {
    const resources = document.querySelectorAll('.resource-card');
    resources.forEach(resource => {
        const title = resource.querySelector('h3').textContent;
        resource.style.display = title.includes(type) ? 'block' : 'none';
    });
    showNotification(`Filtrado por ${type}`);
}

// Download Resource
function downloadResource(fileName) {
    showNotification(`A descarregar ${fileName}...`);
    setTimeout(() => {
        const link = document.createElement('a');
        link.href = `/static/files/${fileName}`;
        link.download = fileName;
        link.click();
    }, 1000);
}

// Preview Resource
function previewResource(fileName) {
    const modal = document.getElementById('filePreviewModal');
    const image = document.getElementById('filePreviewImage');
    if (fileName.endsWith('.png') || fileName.endsWith('.jpg')) {
        image.src = `/static/files/${fileName}`;
        modal.classList.add('active');
    } else {
        showNotification('Pré-visualização não disponível para este tipo de ficheiro.');
    }
}

// Close File Preview
function closeFilePreview() {
    document.getElementById('filePreviewModal').classList.remove('active');
}

// Handle File Upload
function handleFileUpload(files) {
    const file = files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
        showNotification('Ficheiro demasiado grande! Máximo 10MB.');
        return;
    }
    document.getElementById('uploadProgress').classList.add('active');
    setTimeout(() => {
        document.getElementById('uploadProgress').classList.remove('active');
        document.getElementById('dropZone').classList.remove('active');
        showNotification('Ficheiro pronto para carregamento!');
    }, 1500);
}

// Upload Resource
function uploadResource() {
    const title = document.getElementById('resourceTitle').value.trim();
    const type = document.getElementById('resourceType').value;
    const description = document.getElementById('resourceDescription').value.trim();
    const file = document.getElementById('resourceFile').files[0];

    if (!title || !description || !file) {
        showNotification('Por favor, preencha todos os campos e selecione um ficheiro.');
        return;
    }

    const resourceGrid = document.getElementById('resourceGrid');
    const newResource = document.createElement('div');
    newResource.className = 'resource-card';
    newResource.innerHTML = `
        <img src="https://via.placeholder.com/300x150" alt="${title}">
        <h3>${title}</h3>
        <p>${description}</p>
        <div class="resource-meta">
            <span>Por: Utilizador</span>
            <span>${new Date().toLocaleDateString()}</span>
        </div>
        <div class="resource-actions">
            <button class="action-btn" onclick="downloadResource('${file.name}')">Descarregar</button>
            <button class="action-btn" onclick="previewResource('${file.name}')">Pré-visualizar</button>
        </div>
    `;
    resourceGrid.prepend(newResource);
    document.getElementById('resourceTitle').value = '';
    document.getElementById('resourceDescription').value = '';
    document.getElementById('resourceFile').value = '';
    showNotification('Recurso carregado com sucesso!');
}

// Drag-and-Drop Functionality
const dropZone = document.getElementById('dropZone');
const dropArea = document.getElementById('dropArea');

dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('active');
});

dropArea.addEventListener('dragleave', () => {
    dropZone.classList.remove('active');
});

dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFileUpload(files);
    document.getElementById('resourceFile').files = files;
});