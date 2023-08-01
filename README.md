# Futurama system model
[Go to Documentation](docs/_build/html/index.html) (only works if you have the repo locally we need to still host the site)

For the documentation:
1. Download the repo and unzip it
2. find docs/_build/index.html and open it in a browser

## Installation

1. Clone the repository to your local machine (or download the [zip file](https://github.com/FutuRaM-Project/IntegratedModel/archive/refs/heads/main.zip))
2. Run
   > bash auto_install.sh to install everything (may require 'chmod +x auto_install.sh' first)

   Or

   >In the root directory of the repository, run `pip install ./src` to install the package

3. You can now import the package in python with `import futuram as f`
   * See src/examples/ELV to get an idea how it can work
   * See classes for the different objects in the model

## Development

You can install the package in editable mode by running `pip install -e ./src` in the root directory of the repository.
This means that you can make changes to the code and test them live, without having to reinstall the package.

If you make changes to the code, do it in your own branch and make a pull request to the main branch when you are done.


## Overview of the classes in system model
![OverviewOfClassesInTheModel](docs/figures/OverviewOfClassesInTheModel.svg)

## Overview of matter classes in the model
![OverviewOfMatterClassesInTheModel](docs/figures/Matter_classes_in_the_FutuRaM_recovery_model.png)

To do:  
* establish/connect templates for process and product data

* fix the tree map code to get the nested dicts inside the outer ones

* connect the parameters the rest of the model, 
add subclasses to parameters for the different kinds

* create efficient way to solve the model flows
