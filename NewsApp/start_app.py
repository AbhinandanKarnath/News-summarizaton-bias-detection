import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def install_requirements():
    """Install Python requirements if not already installed"""
    try:
        import requests
        import flask
        import bs4
        print("✓ Python dependencies already installed")
    except ImportError:
        print("Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Python dependencies installed")

def start_python_api():
    """Start the Python API server"""
    print("Starting Python API server...")
    try:
        # Change to the utils directory where the API server is located
        os.chdir("src/utils")
        subprocess.run([sys.executable, "api_server.py"], check=True)
    except KeyboardInterrupt:
        print("\nPython API server stopped")
    except Exception as e:
        print(f"Error starting Python API server: {e}")

def start_react_app():
    """Start the React development server"""
    print("Starting React development server...")
    try:
        # Go back to the NewsApp directory
        os.chdir("../..")
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\nReact development server stopped")
    except Exception as e:
        print(f"Error starting React development server: {e}")

def main():
    print("🚀 Starting News App with The Hindu Scraper")
    print("=" * 50)
    
    # Install requirements
    install_requirements()
    
    # Start Python API server in a separate thread
    api_thread = threading.Thread(target=start_python_api, daemon=True)
    api_thread.start()
    
    # Wait a moment for the API server to start
    print("Waiting for API server to start...")
    time.sleep(3)
    
    # Start React app
    start_react_app()

if __name__ == "__main__":
    main() 