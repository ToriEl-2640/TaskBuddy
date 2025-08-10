"""
Error handling hooks for TaskBuddy
Provides comprehensive error handling and recovery.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional

class ErrorHandlingHooks:
    """Hooks for error handling and recovery."""
    
    def __init__(self):
        self.error_log_file = ".kiro/error.log"
        self.backup_dir = ".kiro/backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log errors with timestamp and context."""
        timestamp = datetime.now().isoformat()
        error_entry = f"[{timestamp}] ERROR in {context}: {type(error).__name__}: {str(error)}\n"
        
        os.makedirs(os.path.dirname(self.error_log_file), exist_ok=True)
        with open(self.error_log_file, "a", encoding="utf-8") as f:
            f.write(error_entry)
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create a backup of the specified file."""
        if not os.path.exists(file_path):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{os.path.basename(file_path)}.{timestamp}.backup"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.log_error(e, f"creating backup of {file_path}")
            return None
    
    def restore_from_backup(self, file_path: str, backup_path: str) -> bool:
        """Restore file from backup."""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                print(f"✅ Restored {file_path} from {backup_path}")
                return True
            else:
                print(f"❌ Backup file not found: {backup_path}")
                return False
        except Exception as e:
            self.log_error(e, f"restoring {file_path} from backup")
            return False
    
    def handle_json_corruption(self, file_path: str) -> List[Dict[str, Any]]:
        """Handle JSON file corruption by attempting recovery."""
        print(f"⚠️ JSON corruption detected in {file_path}")
        
        # Try to find the most recent backup
        backups = [f for f in os.listdir(self.backup_dir) if f.startswith(os.path.basename(file_path))]
        if backups:
            latest_backup = max(backups)
            backup_path = os.path.join(self.backup_dir, latest_backup)
            
            if self.restore_from_backup(file_path, backup_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    self.log_error(e, f"loading restored file {file_path}")
        
        # If no backup or restore failed, return empty list
        print(f"⚠️ Could not recover {file_path}, starting with empty data")
        return []
    
    def safe_file_write(self, file_path: str, data: Any) -> bool:
        """Safely write data to file with backup."""
        # Create backup before writing
        if os.path.exists(file_path):
            self.create_backup(file_path)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.log_error(e, f"writing to {file_path}")
            return False

# Global error handling hooks instance
error_handling_hooks = ErrorHandlingHooks()