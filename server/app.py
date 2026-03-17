from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

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