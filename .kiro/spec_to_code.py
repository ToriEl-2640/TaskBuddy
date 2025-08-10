#!/usr/bin/env python3
"""
Spec-to-Code Generator for TaskBuddy
Automatically generates code from specification files.
"""

import os
import json
from typing import Dict, Any, List
from pathlib import Path

# Simple YAML parser for basic YAML files (no external dependencies)
def simple_yaml_load(content: str) -> Dict[str, Any]:
    """Simple YAML parser for basic key-value pairs and lists."""
    result = {}
    current_key = None
    current_list = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if ':' in line and not line.startswith('-'):
            if current_list is not None:
                result[current_key] = current_list
                current_list = None
            
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value:
                result[key] = value
            else:
                current_key = key
                current_list = []
        elif line.startswith('-') and current_list is not None:
            item = line[1:].strip()
            current_list.append(item)
    
    if current_list is not None:
        result[current_key] = current_list
    
    return result

class SpecToCodeGenerator:
    """Generate code from specification files."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.specs_dir = self.project_root / ".kiro" / "specs"
        self.templates_dir = self.project_root / ".kiro" / "templates"
        
    def load_spec(self, spec_file: str) -> Dict[str, Any]:
        """Load a specification file."""
        spec_path = self.specs_dir / spec_file
        
        if spec_path.suffix.lower() == '.yaml' or spec_path.suffix.lower() == '.yml':
            with open(spec_path, 'r', encoding='utf-8') as f:
                return simple_yaml_load(f.read())
        elif spec_path.suffix.lower() == '.json':
            with open(spec_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported spec file format: {spec_path.suffix}")
    
    def generate_api_endpoints(self, spec: Dict[str, Any]) -> str:
        """Generate Flask API endpoints from specification."""
        endpoints = spec.get('api_endpoints', [])
        if not endpoints:
            return ""
            
        code_lines = [
            "# Generated API endpoints",
            "from flask import jsonify, request",
            ""
        ]
        
        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue
                
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            function_name = endpoint.get('function', 'handler')
            description = endpoint.get('description', 'Generated endpoint')
            
            code_lines.extend([
                f"@app.route('{path}', methods=['{method}'])",
                f"def {function_name}():",
                f'    """{description}"""',
                f"    try:",
                f"        tasks = load_tasks()",
                f"        if request.method == 'GET':",
                f"            return jsonify(tasks)",
                f"        elif request.method == 'POST':",
                f"            # TODO: Implement POST logic",
                f"            return jsonify({{'status': 'not implemented'}})",
                f"        elif request.method == 'PUT':",
                f"            # TODO: Implement PUT logic", 
                f"            return jsonify({{'status': 'not implemented'}})",
                f"        elif request.method == 'DELETE':",
                f"            # TODO: Implement DELETE logic",
                f"            return jsonify({{'status': 'not implemented'}})",
                f"    except Exception as e:",
                f"        return jsonify({{'error': str(e)}}), 500",
                ""
            ])
        
        return "\n".join(code_lines)
    
    def generate_hook_stubs(self, spec: Dict[str, Any]) -> str:
        """Generate hook function stubs from specification."""
        hook_events = spec.get('hook_events', [])
        code_lines = []
        
        for event in hook_events:
            hook_name = event.replace('_', '_').lower()
            code_lines.extend([
                f"def {hook_name}(self, *args, **kwargs):",
                f'    """Hook for {event} event."""',
                f"    # TODO: Implement {hook_name} logic",
                f"    pass",
                ""
            ])
        
        return "\n".join(code_lines)
    
    def generate_test_cases(self, spec: Dict[str, Any]) -> str:
        """Generate test cases from specification."""
        features = spec.get('features', [])
        code_lines = [
            "import unittest",
            "from app import app",
            "",
            "class TaskBuddyTestCase(unittest.TestCase):",
            "    def setUp(self):",
            "        self.app = app.test_client()",
            "        self.app.testing = True",
            ""
        ]
        
        for i, feature in enumerate(features):
            test_name = f"test_feature_{i+1}"
            code_lines.extend([
                f"    def {test_name}(self):",
                f'        """Test: {feature}"""',
                f"        # TODO: Implement test for '{feature}'",
                f"        self.assertTrue(True)  # Placeholder",
                ""
            ])
        
        code_lines.extend([
            "if __name__ == '__main__':",
            "    unittest.main()"
        ])
        
        return "\n".join(code_lines)
    
    def generate_from_spec(self, spec_file: str) -> Dict[str, str]:
        """Generate all code artifacts from a specification file."""
        try:
            spec = self.load_spec(spec_file)
            
            generated_code = {}
            
            # Generate API endpoints if specified
            if 'api_endpoints' in spec and spec['api_endpoints']:
                generated_code['api_endpoints.py'] = self.generate_api_endpoints(spec)
            
            # Generate hook stubs if specified
            if 'hook_events' in spec and spec['hook_events']:
                generated_code['hook_stubs.py'] = self.generate_hook_stubs(spec)
            
            # Generate test cases if features are specified
            if 'features' in spec and spec['features']:
                generated_code['test_generated.py'] = self.generate_test_cases(spec)
            
            return generated_code
        except Exception as e:
            print(f"Error generating from spec {spec_file}: {e}")
            return {}
    
    def write_generated_code(self, generated_code: Dict[str, str], output_dir: str = "generated"):
        """Write generated code to files."""
        output_path = self.project_root / output_dir
        output_path.mkdir(exist_ok=True)
        
        for filename, code in generated_code.items():
            file_path = output_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"Generated: {file_path}")

def main():
    """Main entry point for spec-to-code generation."""
    generator = SpecToCodeGenerator()
    
    # Generate from task management spec
    if (generator.specs_dir / "task-management.md").exists():
        print("Found task-management.md spec file")
        # For markdown specs, we'd need a parser - for now, use YAML
    
    # Look for YAML/JSON spec files
    for spec_file in generator.specs_dir.glob("*.yaml"):
        print(f"Processing spec: {spec_file.name}")
        try:
            generated = generator.generate_from_spec(spec_file.name)
            generator.write_generated_code(generated)
        except Exception as e:
            print(f"Error processing {spec_file.name}: {e}")

if __name__ == "__main__":
    main()