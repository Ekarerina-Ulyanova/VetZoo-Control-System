const API_URL = 'http://localhost:5000/api'

let healthChart, vaccinationChart

fetch(`${API_URL}/me`, { credentials: 'include' })
  .then((res) => {
    if (!res.ok) window.location.href = '/login'
    return res.json()
  })
  .then((user) => {
    if (user.role !== 'admin' && user.role !== 'vet') {
      window.location.href = '/'
    } else {
      loadHealthReport()
      loadVaccinationReport()
    }
  })

async function loadHealthReport() {
  const response = await fetch(`${API_URL}/reports/health-status`, {
    credentials: 'include',
  })
  const data = await response.json()

  const ctx = document.getElementById('healthChart').getContext('2d')
  if (healthChart) healthChart.destroy()

  healthChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(data.status_counts),
      datasets: [
        {
          data: Object.values(data.status_counts),
          backgroundColor: [
            '#28a745',
            '#dc3545',
            '#ffc107',
            '#17a2b8',
            '#6c757d',
          ],
        },
      ],
    },
  })

  const speciesDiv = document.getElementById('speciesStats')
  let html = '<table class="table table-sm">'
  html += '<tr><th>Вид</th><th>Всего</th><th>Статусы</th></tr>'

  for (const [species, stats] of Object.entries(data.species_stats)) {
    html += `<tr>
            <td>${species}</td>
            <td>${stats.total}</td>
            <td>${Object.entries(stats.statuses)
              .map(([s, c]) => `${s}: ${c}`)
              .join(', ')}</td>
        </tr>`
  }
  html += '</table>'
  speciesDiv.innerHTML = html
}

async function loadVaccinationReport() {
  const response = await fetch(`${API_URL}/reports/vaccinations`, {
    credentials: 'include',
  })
  const data = await response.json()

  const statsDiv = document.getElementById('vaccinationStats')
  statsDiv.innerHTML = `
        <div class="alert alert-info">
            <strong>Всего прививок:</strong> ${data.total_vaccinations}<br>
            <strong>Охват вакцинацией:</strong> ${data.vaccination_coverage}%
        </div>
    `

  const ctx = document.getElementById('vaccinationChart').getContext('2d')
  if (vaccinationChart) vaccinationChart.destroy()

  vaccinationChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(data.vaccines_by_type),
      datasets: [
        {
          label: 'Количество использований',
          data: Object.values(data.vaccines_by_type),
          backgroundColor: '#17a2b8',
        },
      ],
    },
  })

  const animalsDiv = document.getElementById('animalsWithoutVaccines')
  if (data.animals_without_vaccinations.length === 0) {
    animalsDiv.innerHTML =
      '<p class="text-success">✓ Все животные имеют прививки</p>'
  } else {
    let html = '<ul class="list-group">'
    data.animals_without_vaccinations.forEach((a) => {
      html += `<li class="list-group-item">${a.name} (${a.species})</li>`
    })
    html += '</ul>'
    animalsDiv.innerHTML = html
  }
}
