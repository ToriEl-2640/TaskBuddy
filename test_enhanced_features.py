#!/usr/bin/env python3
"""
Test suite for enhanced TaskBuddy features including hooks and API.
"""

import unittest
import json
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add .kiro to path for hook imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".kiro", "hooks"))

from app import app, load_tasks, save_tasks

class EnhancedFeaturesTestCase(unittest.TestCase):
    """Test cases for enhanced TaskBuddy features."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create temporary tasks file for testing
        self.test_tasks_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_tasks_file.close()
        
        # Patch the TASKS_FILE constant
        self.tasks_file_patcher = patch('app.TASKS_FILE', self.test_tasks_file.name)
        self.tasks_file_patcher.start()
        
        # Initialize with test data
        self.test_tasks = [
            {"title": "Test Task 1", "done": False},
            {"name": "Test Task 2", "done": True}  # Mixed schema for testing
        ]
        save_tasks(self.test_tasks)
    
    def tearDown(self):
        """Clean up test environment."""
        self.tasks_file_patcher.stop()
        if os.path.exists(self.test_tasks_file.name):
            os.unlink(self.test_tasks_file.name)

class APIEndpointsTestCase(EnhancedFeaturesTestCase):
    """Test cases for API endpoints."""
    
    def test_get_all_tasks_api(self):
        """Test GET /api/tasks endpoint."""
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
    
    def test_create_task_api(self):
        """Test POST /api/tasks endpoint."""
        new_task = {"title": "API Test Task"}
        response = self.app.post('/api/tasks', 
                                json=new_task,
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'API Test Task')
        self.assertFalse(data['done'])
    
    def test_create_task_api_invalid(self):
        """Test POST /api/tasks with invalid data."""
        response = self.app.post('/api/tasks', 
                                json={},
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_specific_task_api(self):
        """Test GET /api/tasks/<id> endpoint."""
        response = self.app.get('/api/tasks/0')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('title', data)
    
    def test_get_nonexistent_task_api(self):
        """Test GET /api/tasks/<id> with invalid ID."""
        response = self.app.get('/api/tasks/999')
        self.assertEqual(response.status_code, 404)
    
    def test_update_task_api(self):
        """Test PUT /api/tasks/<id> endpoint."""
        update_data = {"title": "Updated Task", "done": True}
        response = self.app.put('/api/tasks/0',
                               json=update_data,
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Updated Task')
        self.assertTrue(data['done'])
    
    def test_delete_task_api(self):
        """Test DELETE /api/tasks/<id> endpoint."""
        response = self.app.delete('/api/tasks/0')
        self.assertEqual(response.status_code, 200)
        
        # Verify task was deleted
        tasks = load_tasks()
        self.assertEqual(len(tasks), 1)

class DataConsistencyTestCase(EnhancedFeaturesTestCase):
    """Test cases for data consistency hooks."""
    
    def test_schema_normalization(self):
        """Test that mixed schemas are normalized."""
        try:
            from data_consistency import data_consistency_hooks
            
            # Test normalizing a task with 'name' field
            task_with_name = {"name": "Test Task", "done": False}
            normalized = data_consistency_hooks.normalize_task_schema(task_with_name)
            
            self.assertIn('title', normalized)
            self.assertNotIn('name', normalized)
            self.assertEqual(normalized['title'], 'Test Task')
        except ImportError:
            self.skipTest("Data consistency hooks not available")
    
    def test_data_integrity_validation(self):
        """Test data integrity validation."""
        try:
            from data_consistency import data_consistency_hooks
            
            valid_tasks = [
                {"title": "Task 1", "done": False},
                {"title": "Task 2", "done": True}
            ]
            
            invalid_tasks = [
                {"title": "Task 1"},  # Missing 'done'
                {"done": False}       # Missing 'title'
            ]
            
            self.assertTrue(data_consistency_hooks.validate_data_integrity(valid_tasks))
            self.assertFalse(data_consistency_hooks.validate_data_integrity(invalid_tasks))
        except ImportError:
            self.skipTest("Data consistency hooks not available")

class ErrorHandlingTestCase(EnhancedFeaturesTestCase):
    """Test cases for error handling hooks."""
    
    def test_backup_creation(self):
        """Test backup creation functionality."""
        try:
            from error_handling import error_handling_hooks
            
            backup_path = error_handling_hooks.create_backup(self.test_tasks_file.name)
            self.assertIsNotNone(backup_path)
            self.assertTrue(os.path.exists(backup_path))
            
            # Clean up
            if backup_path and os.path.exists(backup_path):
                os.unlink(backup_path)
        except ImportError:
            self.skipTest("Error handling hooks not available")
    
    def test_safe_file_write(self):
        """Test safe file writing with backup."""
        try:
            from error_handling import error_handling_hooks
            
            test_data = [{"title": "Safe Write Test", "done": False}]
            success = error_handling_hooks.safe_file_write(self.test_tasks_file.name, test_data)
            
            self.assertTrue(success)
            
            # Verify data was written correctly
            with open(self.test_tasks_file.name, 'r') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(loaded_data, test_data)
        except ImportError:
            self.skipTest("Error handling hooks not available")

class PerformanceMonitoringTestCase(EnhancedFeaturesTestCase):
    """Test cases for performance monitoring hooks."""
    
    def test_operation_timing(self):
        """Test operation timing functionality."""
        try:
            from performance_monitoring import performance_hooks
            
            operation_id = performance_hooks.start_operation("test_operation")
            self.assertIsNotNone(operation_id)
            
            # Simulate some work
            import time
            time.sleep(0.01)
            
            duration = performance_hooks.end_operation(operation_id)
            self.assertGreater(duration, 0)
        except ImportError:
            self.skipTest("Performance monitoring hooks not available")
    
    def test_performance_report(self):
        """Test performance report generation."""
        try:
            from performance_monitoring import performance_hooks
            
            # Record some test metrics
            performance_hooks.record_metric("test_op", 0.05, "2025-01-01T00:00:00")
            
            report = performance_hooks.get_performance_report()
            self.assertIn('total_operations', report)
        except ImportError:
            self.skipTest("Performance monitoring hooks not available")

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(APIEndpointsTestCase))
    suite.addTest(unittest.makeSuite(DataConsistencyTestCase))
    suite.addTest(unittest.makeSuite(ErrorHandlingTestCase))
    suite.addTest(unittest.makeSuite(PerformanceMonitoringTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)