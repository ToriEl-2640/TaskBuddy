#!/usr/bin/env python3
"""
Comprehensive test suite for TaskBuddy with hook integration.
"""

import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from app import app, load_tasks, save_tasks
from hooks import hooks

class TaskBuddyTestCase(unittest.TestCase):
    """Test cases for TaskBuddy application."""
    
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
        
        # Initialize with empty tasks
        save_tasks([])
    
    def tearDown(self):
        """Clean up test environment."""
        self.tasks_file_patcher.stop()
        if os.path.exists(self.test_tasks_file.name):
            os.unlink(self.test_tasks_file.name)
    
    def test_load_empty_tasks(self):
        """Test loading tasks from empty file."""
        tasks = load_tasks()
        self.assertEqual(tasks, [])
    
    def test_save_and_load_tasks(self):
        """Test saving and loading tasks."""
        test_tasks = [
            {"name": "Test Task 1", "done": False},
            {"name": "Test Task 2", "done": True}
        ]
        save_tasks(test_tasks)
        loaded_tasks = load_tasks()
        self.assertEqual(loaded_tasks, test_tasks)
    
    def test_index_page(self):
        """Test main index page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_add_task_valid(self):
        """Test adding a valid task."""
        response = self.app.post('/add', data={'task': 'New Test Task'})
        self.assertEqual(response.status_code, 302)  # Redirect
        
        tasks = load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['name'], 'New Test Task')
        self.assertFalse(tasks[0]['done'])
    
    def test_add_task_empty(self):
        """Test adding an empty task."""
        response = self.app.post('/add', data={'task': ''})
        self.assertEqual(response.status_code, 302)  # Redirect
        
        tasks = load_tasks()
        self.assertEqual(len(tasks), 0)  # No task should be added
    
    def test_toggle_task(self):
        """Test toggling task completion status."""
        # Add a task first
        save_tasks([{"name": "Toggle Test", "done": False}])
        
        response = self.app.post('/toggle/0')
        self.assertEqual(response.status_code, 204)  # No content
        
        tasks = load_tasks()
        self.assertTrue(tasks[0]['done'])
        
        # Toggle again
        response = self.app.post('/toggle/0')
        tasks = load_tasks()
        self.assertFalse(tasks[0]['done'])
    
    def test_toggle_invalid_index(self):
        """Test toggling with invalid index."""
        save_tasks([{"name": "Test Task", "done": False}])
        
        response = self.app.post('/toggle/999')
        self.assertEqual(response.status_code, 204)  # Should still return 204
        
        tasks = load_tasks()
        self.assertFalse(tasks[0]['done'])  # Should remain unchanged
    
    def test_delete_task(self):
        """Test deleting a task."""
        save_tasks([
            {"name": "Task 1", "done": False},
            {"name": "Task 2", "done": True}
        ])
        
        response = self.app.get('/delete/0')
        self.assertEqual(response.status_code, 302)  # Redirect
        
        tasks = load_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['name'], 'Task 2')
    
    def test_delete_invalid_index(self):
        """Test deleting with invalid index."""
        save_tasks([{"name": "Test Task", "done": False}])
        
        response = self.app.get('/delete/999')
        self.assertEqual(response.status_code, 302)  # Should still redirect
        
        tasks = load_tasks()
        self.assertEqual(len(tasks), 1)  # Task should remain

class HookIntegrationTestCase(unittest.TestCase):
    """Test cases for hook integration."""
    
    def setUp(self):
        """Set up hook testing environment."""
        self.test_task = {"name": "Hook Test Task", "done": False}
    
    @patch('hooks.hooks._log_operation')
    def test_before_task_add_hook(self, mock_log):
        """Test before_task_add hook validation."""
        # Test valid task
        result = hooks.before_task_add(self.test_task.copy())
        self.assertEqual(result['name'], 'Hook Test Task')
        
        # Test invalid task (empty name)
        with self.assertRaises(ValueError):
            hooks.before_task_add({"name": "", "done": False})
    
    @patch('hooks.hooks._log_operation')
    def test_after_task_add_hook(self, mock_log):
        """Test after_task_add hook logging."""
        result = hooks.after_task_add(self.test_task.copy())
        self.assertEqual(result, self.test_task)
        mock_log.assert_called_once_with("TASK_ADDED", self.test_task)
    
    @patch('hooks.hooks._log_operation')
    def test_task_toggle_hooks(self, mock_log):
        """Test task toggle hooks."""
        # Test before toggle
        result = hooks.before_task_toggle(self.test_task.copy(), 0)
        self.assertIsInstance(result['done'], bool)
        
        # Test after toggle
        toggled_task = self.test_task.copy()
        toggled_task['done'] = True
        result = hooks.after_task_toggle(toggled_task, 0)
        self.assertEqual(result, toggled_task)
        mock_log.assert_called_with("TASK_TOGGLED", toggled_task, "- completed")
    
    @patch('hooks.hooks._log_operation')
    def test_task_delete_hooks(self, mock_log):
        """Test task delete hooks."""
        # Test before delete
        result = hooks.before_task_delete(self.test_task.copy(), 0)
        self.assertEqual(result, self.test_task)
        
        # Test after delete
        hooks.after_task_delete(self.test_task.copy(), 0)
        mock_log.assert_called_once_with("TASK_DELETED", self.test_task)

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TaskBuddyTestCase))
    suite.addTest(unittest.makeSuite(HookIntegrationTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)