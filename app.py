from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'backgrounds')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)

@app.route('/')
def index():
    tasks = load_tasks()
    suggested_backgrounds = [
        "/static/backgrounds/bg1.jpg",
        "/static/backgrounds/bg2.jpg",
        "/static/backgrounds/bg3.jpg"
    ]
    return render_template('index.html', tasks=tasks, suggested_backgrounds=suggested_backgrounds)

@app.route('/add', methods=['POST'])
def add_task():
    tasks = load_tasks()
    task_name = request.form['task']
    tasks.append({'name': task_name, 'done': False})
    save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id]['done']
        save_tasks(tasks)
    return ('', 204)

@app.route('/upload_bg', methods=['POST'])
def upload_bg():
    if 'background' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['background']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return jsonify({'image_url': f'/static/backgrounds/{file.filename}'})

if __name__ == '__main__':
    app.run(debug=True)
