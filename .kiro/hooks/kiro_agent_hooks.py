"""
Kiro Agent Hooks for TaskBuddy
Integrates with Kiro's agent system for automated testing and monitoring.
"""

import json
import subprocess
import os
from typing import Dict, Any, List
from datetime import datetime

class KiroAgentHooks:
    """Hooks that integrate with Kiro's agent system."""
    
    def __init__(self):
        self.test_results_file = ".kiro/test_results.json"
        self.metrics_file = ".kiro/metrics.json"
    
    def on_file_save(self, file_path: str) -> None:
        """Hook triggered when a Python file is saved."""
        if file_path.endswith('.py'):
            print(f"[KIRO HOOK] Python file saved: {file_path}")
            self.run_syntax_check(file_path)
            self.update_metrics()
    
    def run_syntax_check(self, file_path: str) -> bool:
        """Run syntax check on Python file."""
        try:
            result = subprocess.run(
                ['python', '-m', 'py_compile', file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Syntax check passed for {file_path}")
                return True
            else:
                print(f"❌ Syntax errors in {file_path}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error running syntax check: {e}")
            return False
    
    def on_task_operation_complete(self, operation: str, task: Dict[str, Any]) -> None:
        """Hook triggered after any task operation completes."""
        self.update_task_metrics(operation, task)
        
        # Trigger automated tests if configured
        if os.getenv('KIRO_AUTO_TEST', 'false').lower() == 'true':
            self.run_automated_tests()
    
    def update_task_metrics(self, operation: str, task: Dict[str, Any]) -> None:
        """Update task operation metrics."""
        metrics = self.load_metrics()
        
        timestamp = datetime.now().isoformat()
        
        if 'task_operations' not in metrics:
            metrics['task_operations'] = []
        
        metrics['task_operations'].append({
            'timestamp': timestamp,
            'operation': operation,
            'task_title': task.get('title', 'Unknown'),
            'task_status': task.get('done', False)
        })
        
        # Keep only last 100 operations
        metrics['task_operations'] = metrics['task_operations'][-100:]
        
        self.save_metrics(metrics)
    
    def run_automated_tests(self) -> None:
        """Run automated tests and save results."""
        print("[KIRO HOOK] Running automated tests...")
        
        try:
            # Run basic functionality tests
            result = subprocess.run(
                ['python', '-m', 'pytest', '-v', '--json-report', '--json-report-file=.kiro/test_results.json'],
                capture_output=True,
                text=True,
                cwd='.'
            )
            
            if result.returncode == 0:
                print("✅ All tests passed")
            else:
                print(f"❌ Some tests failed: {result.stdout}")
                
        except FileNotFoundError:
            print("⚠️ pytest not found, skipping automated tests")
        except Exception as e:
            print(f"Error running tests: {e}")
    
    def load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file."""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving metrics: {e}")
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate a status report for Kiro dashboard."""
        metrics = self.load_metrics()
        
        total_operations = len(metrics.get('task_operations', []))
        recent_operations = [
            op for op in metrics.get('task_operations', [])
            if (datetime.now() - datetime.fromisoformat(op['timestamp'])).days < 1
        ]
        
        return {
            'total_task_operations': total_operations,
            'operations_today': len(recent_operations),
            'last_operation': metrics.get('task_operations', [{}])[-1] if total_operations > 0 else None,
            'system_status': 'healthy' if total_operations > 0 else 'inactive'
        }

# Global Kiro agent hooks instance
kiro_hooks = KiroAgentHooks()