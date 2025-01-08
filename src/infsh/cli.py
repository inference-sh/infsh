import os
import sys
import json
from pathlib import Path
import importlib.util
from typing import Optional
import webbrowser
import yaml
from pydantic import BaseModel, create_model

DEFAULT_YAML_CONTENT = """
name: inference-sh/sample-app  # Change this to your username/appname
repo: https://github.com/inference-sh/sample-app.git  # Change this to your repo
version: 0.1.0
"""

DEFAULT_INFERENCE_CONTENT = """
from pydantic import BaseModel

class PredictInput(BaseModel):
    text: str

class PredictOutput(BaseModel):
    result: str

class Predictor:
    def setup(self):
        \"\"\"Initialize your model and resources here.\"\"\"
        pass

    def predict(self, input_data: PredictInput) -> PredictOutput:
        \"\"\"Run prediction on the input data.\"\"\"
        return PredictOutput(result=f"Processed: {input_data.text}")

    def unload(self):
        \"\"\"Clean up resources here.\"\"\"
        pass
"""

DEFAULT_GITIGNORE_CONTENT = """
# inference.sh
*.infsh
.infsh/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
!.gitignore
!src/
!requirements.txt
!inf.yml
"""

DEFAULT_OPENAPI_CONTENT = """
{
  "openapi": "3.0.0",
  "info": {
    "title": "inference.sh API",
    "version": "1.0.0"
  },
  "paths": {
    "/predict": {
      "post": {
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "properties": {
                  "image": {
                    "title": "Image",
                    "type": "string"
                  },
                  "mask": {
                    "title": "Mask",
                    "type": "string"
                  }
                },
                "required": [
                  "image",
                  "mask"
                ],
                "title": "PredictInput",
                "type": "object"
              }
            }
          }
        }
      }
    }
  }
}
"""

def generate_init_py():
    """Generate __init__.py if it doesn't exist."""
    if os.path.exists("__init__.py"):
        print("✓ __init__.py already exists, skipping...")
        return False
    
    print("Creating __init__.py...")
    with open("__init__.py", "w") as f:
        f.write("")
    print("✓ Created __init__.py")
    return True

def generate_yaml():
    """Generate inf.yml if it doesn't exist."""
    if os.path.exists("inf.yml"):
        with open("inf.yml", "r") as f:
            config = yaml.safe_load(f)
        print("✓ inf.yml already exists with name:", config['name'])
        return False
    
    print("Creating inf.yml...")
    with open("inf.yml", "w") as f:
        f.write(DEFAULT_YAML_CONTENT.strip())
    print("✓ Created inf.yml")
    return True

def generate_inference():
    """Generate inference.py if it doesn't exist."""
    if os.path.exists("inference.py"):
        print("✓ inference.py already exists, skipping...")
        return False
    
    print("Creating inference.py...")
    with open("inference.py", "w") as f:
        f.write(DEFAULT_INFERENCE_CONTENT.strip())
    print("✓ Created inference.py")
    return True

def generate_requirements():
    """Generate requirements.txt if it doesn't exist."""
    if os.path.exists("requirements.txt"):
        print("✓ requirements.txt already exists, skipping...")
        return False
    
    print("Creating requirements.txt...")
    with open("requirements.txt", "w") as f:
        f.write("pydantic>=2.0.0\n")
    print("✓ Created requirements.txt")
    return True

def generate_gitignore():
    """Generate .gitignore if it doesn't exist."""
    if os.path.exists(".gitignore"):
        print("✓ .gitignore already exists, skipping...")
        return False
    
    print("Creating .gitignore...")
    with open(".gitignore", "w") as f:
        f.write(DEFAULT_GITIGNORE_CONTENT.strip())
    print("✓ Created .gitignore")
    return True

def generate_default_openapi():
    """Generate openapi.json if it doesn't exist."""
    if os.path.exists("openapi.json"):
        print("✓ openapi.json already exists, skipping...")
        return False
    
    print("Creating openapi.json...")
    with open("openapi.json", "w") as f:
        f.write(DEFAULT_OPENAPI_CONTENT.strip())
    print("✓ Created openapi.json")
    return True

def create_app():
    """Create a new inference.sh application."""
    generate_yaml()
    generate_inference()
    generate_requirements()
    generate_gitignore()
    generate_default_openapi()
    print("\nSuccessfully created new inference.sh app structure!")

def login():
    """Login to inference.sh (dummy implementation)."""
    # Dummy implementation
    print("Logged in as: test_user")
    return "test_user"

def generate_openapi_schema(module) -> dict:
    """Generate OpenAPI schema from PredictInput and PredictOutput models."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "inference.sh API", "version": "1.0.0"},
        "paths": {
            "/predict": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": module.PredictInput.model_json_schema()
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful prediction",
                            "content": {
                                "application/json": {
                                    "schema": module.PredictOutput.model_json_schema()
                                }
                            }
                        }
                    }
                }
            }
        }
    }

def predeploy():
    """Run predeploy checks and generate OpenAPI schema."""
    try:
        # Generate missing files if needed
        if not os.path.exists("inf.yml"):
            generate_yaml()
        if not os.path.exists("inference.py"):
            generate_inference()
        if not os.path.exists("requirements.txt"):
            generate_requirements()
        if not os.path.exists(".gitignore"):
            generate_gitignore()

        # Use the context manager to handle imports
        with TemporaryPackageStructure() as module:
            print("✓ inference.py can be imported")
            
            # Check required classes and methods
            predictor = module.App()
            if not all(hasattr(predictor, method) for method in ['setup', 'predict', 'unload']):
                print("Error: Predictor must implement setup, predict, and unload methods")
                return False
            print("✓ Predictor implements setup, predict, and unload methods")

            # Verify PredictInput and PredictOutput are valid pydantic models
            if not (isinstance(module.PredictInput, type) and issubclass(module.PredictInput, BaseModel)):
                print("Error: PredictInput must be a Pydantic model")
                return False
            print("✓ PredictInput is a Pydantic model")
            if not (isinstance(module.PredictOutput, type) and issubclass(module.PredictOutput, BaseModel)):
                print("Error: PredictOutput must be a Pydantic model")
                return False
            print("✓ PredictOutput is a Pydantic model")

            # Generate OpenAPI schema
            schema = generate_openapi_schema(module)
            
            with open("openapi.json", "w") as f:
                json.dump(schema, f, indent=2)
            print("✓ OpenAPI schema generated")

            print("✓ Predeploy checks passed.")
            return True

    except Exception as e:
        print("\n❌ Error during predeploy:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        import traceback
        print("\nTraceback:")
        traceback.print_exc()
        return False
    
def deploy():
    """Deploy the app to inference.sh."""
    predeploy()
    print("Deploying app...")
    # Check if git is initialized
    if not os.path.exists(".git"):
        print("Error: Git repository not initialized. Please run 'git init' first.")
        return False
    
    # Check if there are any changes to commit
    import subprocess
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout:
        print("Error: You have uncommitted changes. Please commit all changes before deploying.")
        return False
        
    # Check if remote exists
    try:
        subprocess.run(["git", "remote", "get-url", "origin"], check=True)
        print("✓ Remote repository found")
    except subprocess.CalledProcessError:
        print("Error: Remote repository not found. Please run 'git remote add origin <your-repo-url>' first.")
        return False

    try:
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        print("✓ Code pushed to remote repository")
    except subprocess.CalledProcessError:
        print("Error: Failed to push to remote repository. Please check your git configuration.")
        return False
    print("✓ App deployed")
    return True

class TemporaryPackageStructure:
    def __init__(self, files_to_copy=None):
        self.current_dir = os.getcwd()
        self.infsh_dir = os.path.join(self.current_dir, ".infsh")
        self.temp_dir = os.path.join(self.infsh_dir, "build")
        self.files_to_copy = files_to_copy or ["inference.py", "simple_lama.py"]
        self.module = None

    def __enter__(self):
        # Create .infsh/build structure
        os.makedirs(self.temp_dir, exist_ok=True)
            
        # Copy files
        import shutil
        for file in self.files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, os.path.join(self.temp_dir, file))
        
        # Create __init__.py
        with open(os.path.join(self.temp_dir, "__init__.py"), "w") as f:
            pass
            
        # Set up import path
        if self.infsh_dir not in sys.path:
            sys.path.insert(0, self.infsh_dir)
            
        # Import module
        spec = importlib.util.spec_from_file_location(
            "build.inference",
            os.path.join(self.temp_dir, "inference.py")
        )
        if not spec or not spec.loader:
            raise ImportError("Cannot load inference.py")
            
        self.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.module
        spec.loader.exec_module(self.module)
        
        return self.module

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up build directory but keep .infsh
        import shutil
        shutil.rmtree(self.temp_dir)
        if "build.inference" in sys.modules:
            del sys.modules["build.inference"]
