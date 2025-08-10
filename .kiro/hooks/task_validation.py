"""
Task validation hooks for TaskBuddy
Provides comprehensive validation for task operations.
"""

from typing import Dict, Any, List
import re

class TaskValidationHooks:
    """Validation hooks for task operations."""
    
    def __init__(self):
        self.max_title_length = 200
        self.min_title_length = 1
        self.forbidden_chars = ['<', '>', '&', '"', "'"]
    
    def validate_task_title(self, title: str) -> str:
        """Validate and sanitize task title."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        title = title.strip()
        
        if len(title) < self.min_title_length:
            raise ValueError(f"Task title must be at least {self.min_title_length} character(s)")
        
        if len(title) > self.max_title_length:
            title = title[:self.max_title_length]
        
        # Remove forbidden characters
        for char in self.forbidden_chars:
            title = title.replace(char, '')
        
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title)
        
        return title
    
    def validate_task_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete task data structure."""
        if not isinstance(task_data, dict):
            raise ValueError("Task data must be a dictionary")
        
        # Validate title or name field
        if 'title' in task_data:
            task_data['title'] = self.validate_task_title(task_data['title'])
        elif 'name' in task_data:
            task_data['name'] = self.validate_task_title(task_data['name'])
        
        # Validate done status
        if 'done' in task_data:
            if not isinstance(task_data['done'], bool):
                task_data['done'] = bool(task_data['done'])
        else:
            task_data['done'] = False
        
        return task_data
    
    def validate_task_index(self, index: int, tasks: List[Dict[str, Any]]) -> None:
        """Validate task index is within bounds."""
        if not isinstance(index, int):
            raise ValueError("Task index must be an integer")
        
        if index < 0 or index >= len(tasks):
            raise ValueError(f"Task index {index} is out of range (0-{len(tasks)-1})")

# Global validation hooks instance
validation_hooks = TaskValidationHooks()