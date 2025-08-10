# TaskBuddy Hooks System
from typing import Dict, Any, Optional
import json
import datetime
import os
import sys

# Import additional hook systems
sys.path.append(os.path.join(os.path.dirname(__file__), ".kiro", "hooks"))
try:
    from task_validation import validation_hooks
    from kiro_agent_hooks import kiro_hooks
    from data_consistency import data_consistency_hooks
    from error_handling import error_handling_hooks
    from performance_monitoring import performance_hooks
except ImportError:
    validation_hooks = None
    kiro_hooks = None
    data_consistency_hooks = None
    error_handling_hooks = None
    performance_hooks = None

class TaskHooks:
    """Centralized hook system for TaskBuddy operations."""
    
    def __init__(self):
        self.log_file = "task_operations.log"
    
    def _log_operation(self, operation: str, task: Dict[str, Any], details: str = "") -> None:
        """Log task operations to file with timestamp."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {operation}: {task.get('title', task.get('name', 'Unknown'))} {details}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def before_task_add(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validation hook before adding a task."""
        # Normalize data schema first
        if data_consistency_hooks:
            task_data = data_consistency_hooks.normalize_task_schema(task_data)
        
        # Use validation hooks if available
        if validation_hooks:
            task_data = validation_hooks.validate_task_data(task_data)
        else:
            # Fallback validation
            title = task_data.get('name') or task_data.get('title', '')
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task_data['title'] = title.strip()[:200]
        
        print(f"[VALIDATION] Task ready to add: '{task_data.get('title', 'Unknown')}'")
        return task_data
    
    def after_task_add(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Hook triggered after a task is successfully added."""
        self._log_operation("TASK_ADDED", task)
        print(f"[SUCCESS] Task added: '{task.get('title', 'Unknown')}'")
        
        # Trigger Kiro agent hooks
        if kiro_hooks:
            kiro_hooks.on_task_operation_complete("add", task)
        
        return task
    
    def before_task_toggle(self, task: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validation hook before toggling a task."""
        if not isinstance(task.get('done'), bool):
            task['done'] = False
        
        print(f"[VALIDATION] Task ready to toggle: '{task.get('name', task.get('title', 'Unknown'))}'")
        return task
    
    def after_task_toggle(self, task: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Hook triggered after a task's completion state changes."""
        status = "completed" if task['done'] else "reopened"
        self._log_operation("TASK_TOGGLED", task, f"- {status}")
        print(f"[SUCCESS] Task '{task.get('name', task.get('title', 'Unknown'))}' {status}")
        
        # Trigger Kiro agent hooks
        if kiro_hooks:
            kiro_hooks.on_task_operation_complete("toggle", task)
        
        return task
    
    def before_task_delete(self, task: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validation hook before deleting a task."""
        print(f"[VALIDATION] Task ready to delete: '{task.get('name', task.get('title', 'Unknown'))}'")
        return task
    
    def after_task_delete(self, task: Dict[str, Any], index: int) -> None:
        """Hook triggered after a task is deleted."""
        self._log_operation("TASK_DELETED", task)
        print(f"[SUCCESS] Task deleted: '{task.get('name', task.get('title', 'Unknown'))}'")
        
        # Trigger Kiro agent hooks
        if kiro_hooks:
            kiro_hooks.on_task_operation_complete("delete", task)

# Global hooks instance
hooks = TaskHooks()

# Legacy compatibility functions
def on_task_added(task: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy compatibility wrapper."""
    return hooks.after_task_add(task)

def on_task_toggled(task: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy compatibility wrapper."""
    return hooks.after_task_toggle(task, -1)