#!/usr/bin/env python3
"""
Validation script for tasks.json file.
Called by Kiro agent hooks when tasks.json is modified.
"""

import json
import sys
import os

def validate_tasks_json(file_path="tasks.json"):
    """Validate the structure and content of tasks.json."""
    if not os.path.exists(file_path):
        print(f"✅ {file_path} does not exist (this is okay)")
        return True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        if not isinstance(tasks, list):
            print(f"❌ {file_path} must contain a list of tasks")
            return False
        
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                print(f"❌ Task {i} must be a dictionary")
                return False
            
            if 'title' not in task:
                print(f"❌ Task {i} missing required 'title' field")
                return False
            
            if not isinstance(task['title'], str):
                print(f"❌ Task {i} 'title' must be a string")
                return False
            
            if 'done' not in task:
                print(f"❌ Task {i} missing required 'done' field")
                return False
            
            if not isinstance(task['done'], bool):
                print(f"❌ Task {i} 'done' must be a boolean")
                return False
        
        print(f"✅ {file_path} is valid ({len(tasks)} tasks)")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ {file_path} contains invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "tasks.json"
    success = validate_tasks_json(file_path)
    sys.exit(0 if success else 1)