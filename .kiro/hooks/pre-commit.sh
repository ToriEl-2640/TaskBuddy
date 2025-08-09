#!/bin/bash
# Simple hook to check Python syntax before committing
echo "🔍 Running pre-commit checks..."
python -m py_compile taskbuddy.py
if [ $? -eq 0 ]; then
    echo "✅ Syntax check passed!"
    exit 0
else
    echo "❌ Syntax errors found!"
    exit 1
fi
