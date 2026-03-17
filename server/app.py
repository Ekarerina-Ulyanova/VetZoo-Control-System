import sys
import os
from flask import Flask, render_template

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '../client'),
            static_url_path='',
            template_folder=os.path.join(os.path.dirname(__file__), 'server/templates'))

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

if __name__ == '__main__':
    print("🚀 VetZoo Control Server запускается...")
    app.run(host='0.0.0.0', port=5000, debug=True)