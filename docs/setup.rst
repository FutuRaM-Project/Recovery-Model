Setup and usage
===============

How to use the model
---------------------

See the example scripts in the `examples` folder for more details on how to use the model.

In each example folder, there is a main python script and a folder of input data. The input data folder contains information to define the model in the following files:

- procesess
- flows
- transfer coefficients
- material composition

These files are imported into the model using modules in the subpackage `futuram.utils`. After importing the input data, the model is run, producing data on the recovery of SRMs and impacts of the recovery. The results are saved in the results folder as a set of csv files and figures.

In the future, the model may be developed to export data in the form of a relational database.

Setup
-----

The model is written in Python. You must have Python 3.6 or higher installed to run the model.

**Windows users**

If you are having problems, I recommend you format your hard drive and install Linux. :D

Otherwise, a python problem is probably related to the definition of the PATH variable. Have a look at `this <https://realpython.com/add-python-to-path/>`_ for how to fix it.

You can also try to install the model in a conda environment.

I recommend using Visual Studio Code as an IDE and also installing Git Bash. Then you can manage everything from inside VS code, including virtual environments and everything with github.

Use included virtual environment
---------------------------------

In the main folder there is a virtual environment that can be activated to run the model directly.

On Linux or Mac, run the following command in the terminal:

.. code-block:: bash

   source futuram-venv/bin/activate

On Windows, run the following command in the command prompt:

.. code-block:: bash

   futuram-venv\Scripts\activate.bat

Make your own virtual environment
---------------------------------

If you want to make your own virtual environment, you can do so by running the following commands in the terminal:

.. code-block:: bash

   python3 -m venv futuram-venv

Then activate it as in the previous section.

Install the package 
------------------------------------------------------
(works also in conda environments, but you have to use 'pip install ./src')
Once you have activated the virtual environment, you can install the package by running the following command in the terminal:

.. code-block:: bash

   pip install ./src

If you want to install the package in editable mode, run the following command in the terminal:

.. code-block:: bash

   pip install -e ./src

This will allow you to make changes to the package and use them without having to reinstall the package.

Usage
-----

Now, you can open a python console or and IDE (Visual Studio Code is recommended) and import the package:

.. code-block:: python

   import futuram as f

From here, you can build your own model or explore one of the examples.

.. toctree::
   :maxdepth: 3