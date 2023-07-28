from setuptools import setup, find_packages

setup(
    name='futuram',
    version='0.1.0',
    description='SRM recovery model for the FutuRaM project',
    author='FutuRaM',
    author_email='s.c.mcdowall@cml.leidenuniv.nl',
    url='https://github.com/FutuRaM-Project/IntegratedModel',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'graphviz==0.20.1',
        'openpyxl==3.1.2',
        'pandas==1.5.3',
        'periodictable==1.6.1',
        'plotly==5.14.1',
        'prettytable==3.8.0',
        'setuptools==68.0.0',
        'tabulate==0.9.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
)
