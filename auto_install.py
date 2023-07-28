"""
auto_install.py

This script will install the FutuRaM package and all its dependencies.
It will also create a virtual environment if you want it to.

Options:
    1. Create a new virtual environment
    2. Install the package in editable mode (for development)

Dependencies:
    pip
    venv

Usage:
    python auto_install.py

After installation:
    1. Activate the virtual environment
        on Linux/Mac:   source <venv_dir>/bin/activate
        on Windows:     <venv_dir>\Scripts\activate.bat

        if you created a new virtual environment in this script, the <venv_dir> is printed.

    2. You can now run the example scripts in src/examples
        eg. 
            python src/examples/ELV/scripts/TestModel_ELV.py
        
"""


import sys
import os
import subprocess
import venv


print(f'{"="*80}\n Installing the FutuRaMa package\n{"="*80}\n')

input_venv = input("Do you want to create a new virtual environment? [y/n] ")
input_dev = input(
    "Do you want to install the package in editable mode (for development)? [y/n] "
)


# Function to get the pip executable based on OS
def get_pip_executable(venv_dir):
    if os.name == "nt":
        return os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_dir, "bin", "pip")


# Function to get the site packages directory based on OS
def get_site_packages(venv_dir):
    if os.name == "nt":
        return os.path.join(venv_dir, "Lib", "site-packages")
    else:
        return os.path.join(
            venv_dir, "lib", "python%s" % sys.version[:3], "site-packages"
        )


# Create a virtual environment
if input_venv == "y":
    print("\nCreating a new virtual environment...")
    home_dir = os.path.join(os.path.expanduser("~"), "venvs")
    venv_dir = os.path.join(home_dir, "/futuram_venv")
    if not os.path.isdir(home_dir):
        os.mkdir(home_dir)
    venv.create(venv_dir, with_pip=True)
    print(f"Virtual environment created at {venv_dir}")
    print("\nTo activate the virtual environment, open you terminal and run:")
    print(f"\tLinux/Mac:    source {venv_dir}/bin/activate")
    print(f"\tWindows:      {venv_dir}\\Scripts\\activate.bat")

print(f'\n\n{"*"*30}\n Installing the FutuRaM package...\n{"*"*30}\n')

# Find the site-packages directory within the virtual environment
site_packages = get_site_packages(venv_dir)

# Add the site-packages directory to sys.path
sys.path.append(site_packages)

# Ensure we're using the pip from the virtual environment
pip_executable = get_pip_executable(venv_dir)

# Upgrade pip
subprocess.call([pip_executable, "install", "--upgrade", "pip"])

# Install the dependencies
subprocess.call([pip_executable, "install", "-r", "./src/requirements.txt"])

# Install the package
if input_dev == "n":
    subprocess.call([pip_executable, "install", "./src"])
# Install the package in editable mode
if input_dev == "y":
    subprocess.call([pip_executable, "install", "-e", "./src"])


print(f'\n\n{"*"*30}\n Installation complete!\n{"*"*30}\n')

print(
    """
      To use the package:
    1. Activate the virtual environment
        on Linux/Mac:   source <venv_dir>/bin/activate
        on Windows:     <venv_dir>\Scripts\activate.bat

        if you created a new virtual environment in this script, the <venv_dir> is printed.

    2. You can now run the example scripts in src/examples
        eg. 
            python src/examples/ELV/scripts/TestModel_ELV.py
      """
)

print(f'\n\n{"="*80}\n')
