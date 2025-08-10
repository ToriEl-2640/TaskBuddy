# Task Management Specification

## Overview
TaskBuddy is a Flask-based task management application with hook integration for extensible functionality.

## Core Features

### Task Operations
- **Add Task**: Create new tasks with title and default incomplete status
- **Toggle Task**: Mark tasks as complete/incomplete
- **Delete Task**: Remove tasks from the system
- **List Tasks**: Display all tasks with their current status

### Data Storage
- Tasks stored in `tasks.json` file
- Each task has: `title` (string), `done` (boolean)
- Automatic data persistence on all operations

### Hook Integration
- Pre/post operation hooks for all task operations
- Validation hooks for data integrity
- Logging hooks for monitoring and debugging
- Extensible hook system for future enhancements

## API Endpoints
- `GET /` - Main task interface
- `POST /add` - Add new task
- `POST /toggle/<index>` - Toggle task completion
- `POST /api/toggle/<index>` - AJAX toggle endpoint
- `POST /delete/<index>` - Delete task

## Hook Events
- `before_task_add` - Validation before adding
- `after_task_add` - Actions after successful add
- `before_task_toggle` - Validation before toggle
- `after_task_toggle` - Actions after successful toggle
- `before_task_delete` - Validation before delete
- `after_task_delete` - Actions after successful delete