const API_URL = 'http://localhost:5000/api';
let currentAnimalId = null;

async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/me`, {
            credentials: 'include'
        });
        if (response.ok) {
            const user = await response.json();
            document.getElementById('userDisplay').innerText = 
                `${user.full_name || user.username} (${user.role})`;
            loadAnimals();
        } else {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Ошибка проверки авторизации:', error);
        window.location.href = '/login';
    }
}

async function loadAnimals() {
    try {
        const response = await fetch(`${API_URL}/animals`, {
            credentials: 'include'
        });
        if (!response.ok) throw new Error('Ошибка загрузки');
        const animals = await response.json();
        displayAnimals(animals);
    } catch (error) {
        alert('Ошибка загрузки: ' + error);
    }
}

function displayAnimals(animals) {
    const container = document.getElementById('animalsList');
    if (!container) return;
    
    container.innerHTML = '';
    
    animals.forEach(animal => {
        const card = `
            <div class="col-md-4">
                <div class="card animal-card">
                    <div class="card-body">
                        <h5 class="card-title">${animal.name}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">${animal.species}</h6>
                        <p class="card-text">
                            <small>Вольер: ${animal.enclosure || 'не указан'}</small><br>
                            <span class="status-badge">${animal.health_status}</span>
                        </p>
                        <button class="btn btn-sm btn-primary" onclick="viewAnimal(${animal.id})">
                            Подробнее
                        </button>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += card;
    });
}

async function viewAnimal(id) {
    try {
        const response = await fetch(`${API_URL}/animals/${id}`, {
            credentials: 'include'
        });
        const animal = await response.json();
        
        alert(`Просмотр животного: ${animal.name} (функция в разработке)`);
    } catch (error) {
        alert('Ошибка загрузки: ' + error);
    }
}

document.addEventListener('DOMContentLoaded', checkAuth);

async function viewAnimal(id) {
    currentAnimalId = id;
    try {
        const response = await fetch(`${API_URL}/animals/${id}`, {
            credentials: 'include'
        });
        const animal = await response.json();
        
        document.getElementById('viewAnimalTitle').textContent = `${animal.name} (${animal.species})`;
        document.getElementById('animalInfo').innerHTML = `
            <p><strong>ID:</strong> ${animal.id}</p>
            <p><strong>Дата прибытия:</strong> ${animal.arrival_date}</p>
            <p><strong>Дата рождения:</strong> ${animal.birth_date || 'не указана'}</p>
            <p><strong>Пол:</strong> ${animal.gender || 'не указан'}</p>
            <p><strong>Вольер:</strong> ${animal.enclosure || 'не указан'}</p>
            <p><strong>Примечания:</strong> ${animal.notes || 'нет'}</p>
        `;
        
        await loadExaminations(id);
        await loadVaccinations(id);
        
        // Показать модальное окно
        // ... код открытия модалки
    } catch (error) {
        alert('Ошибка загрузки: ' + error);
    }
}

async function loadExaminations(animalId) {
    const response = await fetch(`${API_URL}/animals/${animalId}/examinations`, {
        credentials: 'include'
    });
    const exams = await response.json();
    
    const container = document.getElementById('examsList');
    if (!container) return;
    
    if (exams.length === 0) {
        container.innerHTML = '<p class="text-muted">Осмотров нет</p>';
        return;
    }
    
    container.innerHTML = exams.map(exam => `
        <div class="timeline-item">
            <div class="timeline-date">${exam.examination_date}</div>
            <div><strong>Ветеринар:</strong> ${exam.veterinarian}</div>
            <div><strong>Диагноз:</strong> ${exam.diagnosis}</div>
            <div><strong>Лечение:</strong> ${exam.treatment}</div>
        </div>
    `).join('');
}

async function loadVaccinations(animalId) {
    const response = await fetch(`${API_URL}/animals/${animalId}/vaccinations`, {
        credentials: 'include'
    });
    const vaccines = await response.json();
    
    const container = document.getElementById('vaccinesList');
    if (!container) return;
    
    if (vaccines.length === 0) {
        container.innerHTML = '<p class="text-muted">Прививок нет</p>';
        return;
    }
    
    container.innerHTML = vaccines.map(v => `
        <div class="timeline-item">
            <div class="timeline-date">${v.vaccination_date}</div>
            <div><strong>Вакцина:</strong> ${v.vaccine_name}</div>
            <div><strong>Ветеринар:</strong> ${v.veterinarian}</div>
            ${v.next_due_date ? `<div><strong>Следующая:</strong> ${v.next_due_date}</div>` : ''}
        </div>
    `).join('');
}
