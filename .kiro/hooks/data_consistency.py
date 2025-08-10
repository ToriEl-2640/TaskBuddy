"""
Data consistency hooks for TaskBuddy
Ensures consistent data schema across the application.
"""

from typing import Dict, Any, List
import json

class DataConsistencyHooks:
    """Hooks to maintain data consistency."""
    
    def normalize_task_schema(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize task schema to use consistent field names."""
        # Convert 'name' to 'title' for consistency
        if 'name' in task and 'title' not in task:
            task['title'] = task.pop('name')
        
        # Ensure required fields exist
        if 'title' not in task:
            task['title'] = 'Untitled Task'
        
        if 'done' not in task:
            task['done'] = False
        
        return task
    
    def normalize_all_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize all tasks in the list."""
        return [self.normalize_task_schema(task) for task in tasks]
    
    def validate_data_integrity(self, tasks: List[Dict[str, Any]]) -> bool:
        """Validate data integrity across all tasks."""
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                print(f"❌ Task {i} is not a dictionary")
                return False
            
            if 'title' not in task:
                print(f"❌ Task {i} missing title field")
                return False
            
            if 'done' not in task:
                print(f"❌ Task {i} missing done field")
                return False
            
            if not isinstance(task['title'], str):
                print(f"❌ Task {i} title is not a string")
                return False
            
            if not isinstance(task['done'], bool):
                print(f"❌ Task {i} done is not a boolean")
                return False
        
        return True

# Global data consistency hooks instance
data_consistency_hooks = DataConsistencyHooks()