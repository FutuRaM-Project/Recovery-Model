#!/bin/bash
# Script to update the futuram package
package_name="futuram"
echo
echo "===================================================="
echo "         Updating $package_name package"
echo "===================================================="

sleep 1


echo "---------------------------"
if [ -d ~/venvs/futuram-dev ]; then
    source ~/venvs/futuram-dev/bin/activate
    echo "Activated futuram-dev virtual environment"
else
    echo "futuram-dev virtual environment does not exist"
fi
echo "---------------------------"


echo
echo "---------------------------"
echo "   Updating dependencies"
echo "---------------------------"

pip install pipreqs
pip install --upgrade setuptools
pip install --upgrade wheel

if [ $? -ne 0 ]; then
    echo "Error updating dependencies"
    exit 1
fi
echo "---------------------------"
echo "   Dependencies updated"
echo "---------------------------"

echo "-------------------------------------"
echo "   Recreating distribution files"
echo "-------------------------------------" 

# Create the distribution
python setup.py clean
python setup.py sdist bdist_wheel
if [ $? -ne 0 ]; then
    echo "Error creating distribution"
    exit 1
fi

# Generate the requirements.txt file
pipreqs . --force
if [ $? -ne 0 ]; then
    echo "Error generating requirements.txt"
    exit 1
fi

# Install the requirements
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing requirements"
    exit 1
fi

# Print the location of the distribution files and updated files
echo "-------------------------------------------------------"
echo "   Distribution files created in $(pwd)/dist"
echo "   requirements.txt and setup.py files updated"
echo "-------------------------------------------------------"

echo "===================================================="
echo "         Updated $package_name package"
echo "===================================================="
echo