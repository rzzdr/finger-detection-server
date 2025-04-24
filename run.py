#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def check_poetry():
    """Check if Poetry is installed."""
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_poetry():
    """Install Poetry based on the platform."""
    print("Poetry not found. Installing Poetry...")
    
    if platform.system() == "Windows":
        # Windows installation
        command = "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
        subprocess.run(["powershell", "-Command", command], check=True)
    else:
        # Unix/Linux/Mac installation
        command = "curl -sSL https://install.python-poetry.org | python3 -"
        subprocess.run(command, shell=True, check=True)
    
    print("Poetry installed successfully!")

def install_dependencies():
    """Install project dependencies using Poetry."""
    print("Installing project dependencies...")
    subprocess.run(["poetry", "install"], check=True)
    print("Dependencies installed successfully!")

def run_server():
    """Run the FastAPI server using Poetry."""
    print("Starting the Finger Detection Server...")
    subprocess.run(["poetry", "run", "python", "main.py"])

def main():
    """Main function to install dependencies and run the server."""
    print("=== Finger Detection Server Setup ===")
    
    if not check_poetry():
        install_poetry()
    
    install_dependencies()
    run_server()

if __name__ == "__main__":
    main()