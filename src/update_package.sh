#!/bin/bash

package_name="FutuRaM-RecoveryModel"

# Create the distribution
python setup.py sdist bdist_wheel

# Generate the requirements.txt file
pipreqs .

# Update the setup.py file based on the requirements.txt file
pip-compile --output-file=- requirements.txt | grep -v '^-r' > setup.py

# Print the location of the distribution files and updated files
echo "Distribution files created in $(pwd)/dist"
echo "requirements.txt and setup.py files updated"
