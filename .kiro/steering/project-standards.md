# TaskBuddy Project Standards

## Code Style Guidelines
- Use clear, descriptive variable names
- Keep functions focused on single responsibilities
- Add docstrings to all functions
- Use type hints where appropriate
- Follow PEP 8 style guidelines

## Architecture Principles
- Maintain separation between data layer (JSON storage) and presentation layer (Flask routes)
- Use hooks for cross-cutting concerns (logging, notifications, validation)
- Keep the codebase beginner-friendly while maintaining professional standards

## Testing Standards
- Write unit tests for core functionality
- Test hook integrations
- Validate JSON data persistence
- Test API endpoints

## Hook Integration
- Use hooks for task lifecycle events (add, toggle, delete)
- Implement validation hooks for data integrity
- Add logging hooks for debugging and monitoring