import sys
import os
from flask import Flask, render_template
from flask_cors import CORS

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '../client'),
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(__file__), 'server/templates'))
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

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

if __name__ == '__main__':
    print("🚀 VetZoo Control Server запускается...")
    app.run(host='0.0.0.0', port=5000, debug=True)

