import sys
import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '../client'),
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(__file__), 'server/templates'))
CORS(app)

app.secret_key = 'super-secret-key-vetzoo'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, role, full_name):
        self.id = user_id
        self.username = username
        self.role = role
        self.full_name = full_name

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user(user_id)
    if user_data:
        return User(
            user_id=user_data[0],
            username=user_data[1],
            role=user_data[4],
            full_name=user_data[3]
        )
    return None

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Требуется авторизация'}), 401
            if current_user.role not in roles:
                return jsonify({'error': 'Недостаточно прав'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_default_admin():
    admin = db.get_user_by_username('admin')
    if not admin:
        pwd_hash = generate_password_hash('admin')
        db.create_user('admin', pwd_hash, 'admin', 'Default Admin')
        print("✅ Администратор по умолчанию создан: admin / admin")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = db.get_user_by_username(username)
        
        if user_data and check_password_hash(user_data[2], password):
            user = User(
                user_id=user_data[0],
                username=user_data[1],
                role=user_data[4],
                full_name=user_data[3]
            )
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
            return render_template('login.html'), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'role': current_user.role,
        'full_name': current_user.full_name
    })

@app.route('/api/users', methods=['GET'])
@login_required
@role_required('admin')
def get_users():
    users = db.get_all_users()
    result = []
    for u in users:
        result.append({
            'id': u[0],
            'username': u[1],
            'full_name': u[2],
            'role': u[3],
            'created_at': u[4]
        })
    return jsonify(result)

@app.route('/api/users', methods=['POST'])
@login_required
@role_required('admin')
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    full_name = data.get('full_name', '')

    if not username or not password or role not in ['vet', 'keeper']:
        return jsonify({'error': 'Неверные данные'}), 400

    existing = db.get_user_by_username(username)
    if existing:
        return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400

    pwd_hash = generate_password_hash(password)
    user_id = db.create_user(username, pwd_hash, role, full_name)
    if user_id:
        return jsonify({'id': user_id, 'message': 'Пользователь создан'}), 201
    return jsonify({'error': 'Ошибка создания'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Нельзя удалить себя'}), 400
    success = db.delete_user(user_id)
    if success:
        return jsonify({'message': 'Пользователь удалён'})
    return jsonify({'error': 'Пользователь не найден'}), 404


@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

@app.route('/api/animals', methods=['GET'])
def get_animals():
    try:
        animals = db.get_all_animals()
        result = []
        for a in animals:
            result.append({
                'id': a[0], 'name': a[1], 'species': a[2], 'arrival_date': a[3],
                'birth_date': a[4], 'gender': a[5], 'enclosure': a[6],
                'health_status': a[7], 'notes': a[8]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/animals', methods=['POST'])
@login_required
@role_required('vet')
def add_animal():
    try:
        data = request.json
        animal_id = db.add_animal(
            data['name'],
            data['species'],
            data.get('arrival_date', datetime.now().strftime('%Y-%m-%d')),
            data.get('birth_date'),
            data.get('gender'),
            data.get('enclosure'),
            data.get('notes')
        )
        return jsonify({'id': animal_id, 'message': 'Животное добавлено'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animals/<int:animal_id>/status', methods=['PUT'])
@login_required
@role_required('vet')
def update_animal_status(animal_id):
    try:
        data = request.json
        if not db.get_animal(animal_id):
            return jsonify({'error': 'Животное не найдено'}), 404
        db.update_animal_status(animal_id, data['status'])
        return jsonify({'message': 'Статус обновлён'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/animals/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    try:
        animal = db.get_animal(animal_id)
        if not animal:
            return jsonify({'error': 'Животное не найдено'}), 404
        return jsonify({
            'id': animal[0], 'name': animal[1], 'species': animal[2],
            'arrival_date': animal[3], 'birth_date': animal[4], 'gender': animal[5],
            'enclosure': animal[6], 'health_status': animal[7], 'notes': animal[8]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/animals/<int:animal_id>/examinations', methods=['GET'])
@login_required
def get_examinations(animal_id):
    try:
        exams = db.get_animal_examinations(animal_id)
        result = []
        for e in exams:
            result.append({
                'id': e[0], 'animal_id': e[1], 'examination_date': e[2],
                'veterinarian': e[3], 'diagnosis': e[4], 'treatment': e[5],
                'notes': e[6], 'is_scheduled': e[7] if len(e) > 7 else 0
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/examinations', methods=['POST'])
@login_required
@role_required('vet')
def add_examination():
    try:
        data = request.json
        exam_id = db.add_examination(
            data['animal_id'],
            data.get('examination_date', datetime.now().strftime('%Y-%m-%d %H:%M')),
            data['veterinarian'],
            data['diagnosis'],
            data['treatment'],
            data.get('notes'),
            data.get('is_scheduled', 0)
        )
        return jsonify({'id': exam_id, 'message': 'Осмотр добавлен'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/animals/<int:animal_id>/vaccinations', methods=['GET'])
@login_required
def get_vaccinations(animal_id):
    try:
        vaccines = db.get_animal_vaccinations(animal_id)
        result = []
        for v in vaccines:
            result.append({
                'id': v[0], 'animal_id': v[1], 'vaccination_date': v[2],
                'vaccine_name': v[3], 'veterinarian': v[4], 'next_due_date': v[5],
                'is_scheduled': v[6] if len(v) > 6 else 0
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vaccinations', methods=['POST'])
@login_required
@role_required('vet')
def add_vaccination():
    try:
        data = request.json
        vacc_id = db.add_vaccination(
            data['animal_id'],
            data.get('vaccination_date', datetime.now().strftime('%Y-%m-%d')),
            data['vaccine_name'],
            data['veterinarian'],
            data.get('next_due_date'),
            data.get('is_scheduled', 0)
        )
        return jsonify({'id': vacc_id, 'message': 'Прививка добавлена'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/examinations/<int:exam_id>/complete', methods=['PUT'])
@login_required
@role_required('vet')
def complete_examination(exam_id):
    try:
        success = db.complete_examination(exam_id)
        if success:
            return jsonify({'message': 'Осмотр отмечен как проведенный'})
        return jsonify({'error': 'Осмотр не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vaccinations/<int:vacc_id>/complete', methods=['PUT'])
@login_required
@role_required('vet')
def complete_vaccination(vacc_id):
    try:
        success = db.complete_vaccination(vacc_id)
        if success:
            return jsonify({'message': 'Прививка отмечена как проведенная'})
        return jsonify({'error': 'Прививка не найдена'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 VetZoo Control Server запускается...")
    app.run(host='0.0.0.0', port=5000, debug=True)

