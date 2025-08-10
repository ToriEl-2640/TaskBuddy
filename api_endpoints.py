# Generated API endpoints for TaskBuddy
from flask import jsonify, request
from app import app, load_tasks, save_tasks
from hooks import hooks

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Retrieve all tasks"""
    try:
        tasks = load_tasks()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        task_data = {'title': data['title'], 'done': False}
        
        # Run pre-add hook
        if hooks:
            task_data = hooks.before_task_add(task_data)
        
        tasks = load_tasks()
        tasks.append(task_data)
        save_tasks(tasks)
        
        # Run post-add hook
        if hooks:
            hooks.after_task_add(task_data)
        
        return jsonify(task_data), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Retrieve a specific task"""
    try:
        tasks = load_tasks()
        if 0 <= task_id < len(tasks):
            return jsonify(tasks[task_id])
        return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a specific task"""
    try:
        tasks = load_tasks()
        if not (0 <= task_id < len(tasks)):
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update task fields
        if 'title' in data:
            tasks[task_id]['title'] = data['title']
        if 'done' in data:
            tasks[task_id]['done'] = bool(data['done'])
        
        save_tasks(tasks)
        return jsonify(tasks[task_id])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_api(task_id):
    """Delete a specific task"""
    try:
        tasks = load_tasks()
        if not (0 <= task_id < len(tasks)):
            return jsonify({'error': 'Task not found'}), 404
        
        task_to_delete = tasks[task_id].copy()
        
        # Run pre-delete hook
        if hooks:
            hooks.before_task_delete(task_to_delete, task_id)
        
        tasks.pop(task_id)
        save_tasks(tasks)
        
        # Run post-delete hook
        if hooks:
            hooks.after_task_delete(task_to_delete, task_id)
        
        return jsonify({'message': 'Task deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500