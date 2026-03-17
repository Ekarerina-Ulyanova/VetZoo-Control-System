const API_URL = 'http://localhost:5000/api';

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