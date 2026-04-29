from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
import json
import os
from functools import wraps
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Simple JSON-based database (for demo purposes)
TASKS_FILE = 'tasks.json'

def load_tasks():
    """Load tasks from JSON file"""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Initialize tasks if not exists
if not os.path.exists(TASKS_FILE):
    sample_tasks = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Learn Docker',
            'description': 'Complete Docker tutorial and containerize applications',
            'status': 'completed',
            'priority': 'high',
            'category': 'Learning',
            'due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Build Python Project',
            'description': 'Create a task management system with Flask',
            'status': 'in-progress',
            'priority': 'high',
            'category': 'Development',
            'due_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Write Documentation',
            'description': 'Create comprehensive documentation for the project',
            'status': 'pending',
            'priority': 'medium',
            'category': 'Documentation',
            'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Deploy with Docker',
            'description': 'Deploy the application using Docker Compose',
            'status': 'pending',
            'priority': 'low',
            'category': 'DevOps',
            'due_date': (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    save_tasks(sample_tasks)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task"""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.json
    
    task = {
        'id': str(uuid.uuid4()),
        'title': data.get('title'),
        'description': data.get('description', ''),
        'status': data.get('status', 'pending'),
        'priority': data.get('priority', 'medium'),
        'category': data.get('category', 'General'),
        'due_date': data.get('due_date'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    
    return jsonify(task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    data = request.json
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            task.update({
                'title': data.get('title', task['title']),
                'description': data.get('description', task['description']),
                'status': data.get('status', task['status']),
                'priority': data.get('priority', task['priority']),
                'category': data.get('category', task['category']),
                'due_date': data.get('due_date', task['due_date'])
            })
            save_tasks(tasks)
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/api/tasks/<task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    """Update only task status"""
    data = request.json
    new_status = data.get('status')
    
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = new_status
            save_tasks(tasks)
            return jsonify(task)
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    tasks = load_tasks()
    
    total = len(tasks)
    completed = len([t for t in tasks if t['status'] == 'completed'])
    in_progress = len([t for t in tasks if t['status'] == 'in-progress'])
    pending = len([t for t in tasks if t['status'] == 'pending'])
    
    # Priority breakdown
    high_priority = len([t for t in tasks if t['priority'] == 'high' and t['status'] != 'completed'])
    medium_priority = len([t for t in tasks if t['priority'] == 'medium' and t['status'] != 'completed'])
    low_priority = len([t for t in tasks if t['priority'] == 'low' and t['status'] != 'completed'])
    
    # Category breakdown
    categories = {}
    for task in tasks:
        cat = task.get('category', 'General')
        categories[cat] = categories.get(cat, 0) + 1
    
    return jsonify({
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': round((completed / total * 100) if total > 0 else 0),
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'categories': categories
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
