#!/usr/bin/env python3
"""
Setup script for Harmonização AI RAG System.

This script helps set up the environment and install dependencies.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error output: {result.stderr}")
        return False
    
    if result.stdout:
        print(result.stdout)
    
    return True


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def setup_virtual_environment():
    """Set up virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    if not run_command(f"{sys.executable} -m venv venv"):
        return False
    
    print("✓ Virtual environment created")
    return True


def get_pip_command():
    """Get the correct pip command for the platform."""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        return "venv/bin/pip"


def install_dependencies():
    """Install Python dependencies."""
    pip_cmd = get_pip_command()
    
    print("Upgrading pip...")
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        return False
    
    print("Installing dependencies...")
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        print("Warning: Some dependencies might have failed to install.")
        print("You may need to install additional system dependencies.")
        return False
    
    print("✓ Dependencies installed")
    return True


def setup_environment_file():
    """Set up environment configuration file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from .env.example")
        print("Please edit .env file with your API keys and configuration")
        return True
    else:
        print("Warning: .env.example not found")
        return False


def create_data_directories():
    """Create necessary data directories."""
    directories = [
        "data",
        "data/documents",
        "data/vectorstore",
        "data/vectorstore/chroma",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Data directories created")
    return True


def download_models():
    """Download default models (optional)."""
    print("Downloading default embedding model (this may take a while)...")
    
    # This would download the sentence-transformers model
    download_script = '''
import sys
sys.path.append('.')
from app.rag.embeddings.sentence_transformer import SentenceTransformerEmbedding

print("Downloading all-MiniLM-L6-v2 model...")
embedding_service = SentenceTransformerEmbedding("all-MiniLM-L6-v2")
print("Model downloaded successfully!")
'''
    
    try:
        if os.name == 'nt':  # Windows
            python_cmd = "venv\\Scripts\\python"
        else:  # Unix/Linux/Mac
            python_cmd = "venv/bin/python"
        
        result = subprocess.run(
            [python_cmd, "-c", download_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Default models downloaded")
        else:
            print("Warning: Could not download models automatically")
            print("Models will be downloaded on first use")
    
    except Exception as e:
        print(f"Warning: Could not download models: {e}")
        print("Models will be downloaded on first use")
    
    return True


def verify_installation():
    """Verify the installation."""
    print("Verifying installation...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    # Test imports
    test_script = '''
try:
    from app.main import app
    print("✓ FastAPI app imports successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)

try:
    from app.rag.embeddings.service import get_embedding_service
    print("✓ RAG services import successfully")
except ImportError as e:
    print(f"✗ RAG import error: {e}")
    exit(1)

print("✓ Installation verification passed")
'''
    
    result = subprocess.run(
        [python_cmd, "-c", test_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print("Installation verification failed:")
        print(result.stderr)
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🚀 INSTALLATION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys:")
    print("   - Add your GROQ_API_KEY")
    print("   - Optionally add OPENAI_API_KEY for OpenAI embeddings")
    print()
    print("2. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
    print()
    print("3. Start the server:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8002")
    print()
    print("4. Access the API documentation:")
    print("   http://localhost:8002/docs")
    print()
    print("5. Teste o sistema de cadastro de clientes:")
    print("   - Cadastre um cliente via /v1/cliente")
    print()
    print("For more information, see the README.md file.")
    print("="*60)


def main():
    """Main setup function."""
    print("🔧 Harmonização AI - RAG System Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating environment file", setup_environment_file),
        ("Creating data directories", create_data_directories),
        ("Downloading models (optional)", download_models),
        ("Verifying installation", verify_installation),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"✗ Failed: {step_name}")
            print("Setup incomplete. Please check the errors above.")
            sys.exit(1)
    
    print_next_steps()


if __name__ == "__main__":
    main()