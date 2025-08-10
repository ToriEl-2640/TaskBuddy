"""
Performance monitoring hooks for TaskBuddy
Tracks performance metrics and system health.
"""

import time
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from functools import wraps

class PerformanceMonitoringHooks:
    """Hooks for monitoring application performance."""
    
    def __init__(self):
        self.metrics_file = ".kiro/performance_metrics.json"
        self.current_operations = {}
    
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation."""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        self.current_operations[operation_id] = {
            'name': operation_name,
            'start_time': time.time(),
            'timestamp': datetime.now().isoformat()
        }
        return operation_id
    
    def end_operation(self, operation_id: str) -> float:
        """End timing an operation and record metrics."""
        if operation_id not in self.current_operations:
            return 0.0
        
        operation = self.current_operations.pop(operation_id)
        duration = time.time() - operation['start_time']
        
        # Record the metric
        self.record_metric(operation['name'], duration, operation['timestamp'])
        
        return duration
    
    def record_metric(self, operation: str, duration: float, timestamp: str) -> None:
        """Record a performance metric."""
        metrics = self.load_metrics()
        
        if 'operations' not in metrics:
            metrics['operations'] = []
        
        metrics['operations'].append({
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': timestamp
        })
        
        # Keep only last 1000 operations
        metrics['operations'] = metrics['operations'][-1000:]
        
        # Update summary statistics
        self.update_summary_stats(metrics, operation, duration)
        
        self.save_metrics(metrics)
    
    def update_summary_stats(self, metrics: Dict[str, Any], operation: str, duration: float) -> None:
        """Update summary statistics for operations."""
        if 'summary' not in metrics:
            metrics['summary'] = {}
        
        if operation not in metrics['summary']:
            metrics['summary'][operation] = {
                'count': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'min_duration': float('inf'),
                'max_duration': 0.0
            }
        
        stats = metrics['summary'][operation]
        stats['count'] += 1
        stats['total_duration'] += duration
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        stats['min_duration'] = min(stats['min_duration'], duration)
        stats['max_duration'] = max(stats['max_duration'], duration)
    
    def load_metrics(self) -> Dict[str, Any]:
        """Load performance metrics from file."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save performance metrics to file."""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving performance metrics: {e}")
    
    def monitor_operation(self, operation_name: str):
        """Decorator to monitor operation performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                operation_id = self.start_operation(operation_name)
                try:
                    result = func(*args, **kwargs)
                    duration = self.end_operation(operation_id)
                    print(f"⏱️ {operation_name} completed in {duration*1000:.2f}ms")
                    return result
                except Exception as e:
                    self.end_operation(operation_id)
                    raise
            return wrapper
        return decorator
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report."""
        metrics = self.load_metrics()
        
        if 'summary' not in metrics:
            return {'message': 'No performance data available'}
        
        report = {
            'total_operations': sum(stats['count'] for stats in metrics['summary'].values()),
            'operations_summary': {}
        }
        
        for operation, stats in metrics['summary'].items():
            report['operations_summary'][operation] = {
                'count': stats['count'],
                'avg_duration_ms': round(stats['avg_duration'] * 1000, 2),
                'min_duration_ms': round(stats['min_duration'] * 1000, 2),
                'max_duration_ms': round(stats['max_duration'] * 1000, 2)
            }
        
        return report

# Global performance monitoring hooks instance
performance_hooks = PerformanceMonitoringHooks()