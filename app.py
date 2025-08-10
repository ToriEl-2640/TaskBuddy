from flask import Flask, render_template, request, redirect, url_for, jsonify
from typing import List, Dict, Any
import os
import json
import sys

# Import hooks system
try:
    from hooks import hooks
except ImportError:
    print("Warning: Hooks system not available")
    hooks = None

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'backgrounds')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

TASKS_FILE = 'tasks.json'

def load_tasks() -> List[Dict[str, Any]]:
    """Load tasks from JSON file with data validation."""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
                
                # Normalize task structure using hooks
                try:
                    sys.path.append(os.path.join(os.path.dirname(__file__), ".kiro", "hooks"))
                    from data_consistency import data_consistency_hooks
                    tasks = data_consistency_hooks.normalize_all_tasks(tasks)
                except ImportError:
                    # Fallback normalization
                    for task in tasks:
                        if 'name' in task and 'title' not in task:
                            task['title'] = task.pop('name')
                        if 'done' not in task:
                            task['done'] = False
                
                return tasks
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading tasks: {e}")
            # Try to recover from backup if hooks are available
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), ".kiro", "hooks"))
                from error_handling import error_handling_hooks
                return error_handling_hooks.handle_json_corruption(TASKS_FILE)
            except ImportError:
                pass
            return []
    return []

def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """Save tasks to JSON file with error handling."""
    try:
        # Use safe file write if error handling hooks are available
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), ".kiro", "hooks"))
            from error_handling import error_handling_hooks
            if not error_handling_hooks.safe_file_write(TASKS_FILE, tasks):
                raise IOError("Failed to save tasks using safe write")
        except ImportError:
            # Fallback to direct write
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving tasks: {e}")
        raise

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
    """Add a new task with hook integration."""
    task_name = request.form.get('task')
    if not task_name:
        return redirect(url_for('index'))
    
    try:
        # Prepare task data
        task_data = {'name': task_name, 'done': False}
        
        # Run pre-add hook
        if hooks:
            task_data = hooks.before_task_add(task_data)
        
        # Add task to storage
        tasks = load_tasks()
        tasks.append(task_data)
        save_tasks(tasks)
        
        # Run post-add hook
        if hooks:
            hooks.after_task_add(task_data)
            
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Error adding task: {e}")
        
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id: int):
    """Delete a task with hook integration."""
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        try:
            task_to_delete = tasks[task_id].copy()
            
            # Run pre-delete hook
            if hooks:
                hooks.before_task_delete(task_to_delete, task_id)
            
            # Delete task
            tasks.pop(task_id)
            save_tasks(tasks)
            
            # Run post-delete hook
            if hooks:
                hooks.after_task_delete(task_to_delete, task_id)
                
        except Exception as e:
            print(f"Error deleting task: {e}")
            
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id: int):
    """Toggle task completion status with hook integration."""
    tasks = load_tasks()
    if 0 <= task_id < len(tasks):
        try:
            # Run pre-toggle hook
            if hooks:
                tasks[task_id] = hooks.before_task_toggle(tasks[task_id], task_id)
            
            # Toggle task status
            tasks[task_id]['done'] = not tasks[task_id]['done']
            save_tasks(tasks)
            
            # Run post-toggle hook
            if hooks:
                hooks.after_task_toggle(tasks[task_id], task_id)
                
        except Exception as e:
            print(f"Error toggling task: {e}")
            
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