#!/usr/bin/env python3
"""
AnkiQuest Development Setup Script
Run this to set up your development environment
"""

import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Ensure Python 3.9+"""
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9+ required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"OK: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def create_venv():
    """Create virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("OK: Virtual environment already exists")
        return
    
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("OK: Virtual environment created")

def get_pip_path():
    """Get pip executable path based on OS"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_dependencies():
    """Install required packages"""
    pip = get_pip_path()
    
    print("Installing production dependencies...")
    subprocess.run([str(pip), "install", "-r", "requirements.txt"], check=True)
    
    print("Installing development dependencies...")
    subprocess.run([str(pip), "install", "-r", "requirements-dev.txt"], check=True)
    
    print("OK: Dependencies installed")

def create_directories():
    """Create necessary directories"""
    dirs = [
        "core",
        "data", 
        "ui/animations",
        "integration",
        "assets/mario/characters",
        "assets/mario/items",
        "assets/mario/enemies",
        "assets/mario/backgrounds",
        "assets/mario/ui",
        "assets/sounds",
        "assets/fonts",
        "tests",
        "docs",
        "scripts"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for Python packages
        if not dir_path.startswith("assets") and not dir_path in ["tests", "docs", "scripts"]:
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("OK: Directory structure created")

def create_git_ignore():
    """Create .gitignore if it doesn't exist"""
    gitignore_path = Path(".gitignore")
    
    if gitignore_path.exists():
        print("OK: .gitignore already exists")
        return
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# PyQt
*.ui
*.qrc

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Anki
*.anki2
*.anki21
collection.anki2

# Database
*.db
*.sqlite
*.sqlite3

# Backups
backups/
saves/

# OS
.DS_Store
Thumbs.db

# Build
build/
dist/
*.egg-info/
"""
    
    gitignore_path.write_text(gitignore_content.strip())
    print("OK: .gitignore created")

def create_pytest_ini():
    """Create pytest configuration"""
    pytest_ini = Path("pytest.ini")
    
    if pytest_ini.exists():
        return
    
    content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --cov=core
    --cov=data
    --cov=ui
    --cov-report=html
    --cov-report=term-missing
"""
    
    pytest_ini.write_text(content.strip())
    print("OK: pytest.ini created")

def main():
    print("AnkiQuest Development Setup")
    print("=" * 50)
    
    check_python_version()
    create_venv()
    install_dependencies()
    create_directories()
    create_git_ignore()
    create_pytest_ini()
    
    print("\n" + "=" * 50)
    print("OK: Setup complete!")
    print("\nNext steps:")
    print("   1. Activate virtual environment:")
    
    if platform.system() == "Windows":
        print("      .\\venv\\Scripts\\activate")
    else:
        print("      source venv/bin/activate")
    
    print("   2. Run tests:")
    print("      pytest")
    print("   3. Start development:")
    print("      python -m ankiquest")
    print("\nTip: Use 'black .' to format code before committing")

if __name__ == "__main__":
    main()