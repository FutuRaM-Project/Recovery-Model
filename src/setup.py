from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='futuram',
    version='0.1.0',
    description='SRM recovery model for the FutuRaM project',
    author='FutuRaM',
    author_email='s.c.mcdowall@cml.leidenuniv.nl',
    url='https://github.com/FutuRaM-Project/IntegratedModel',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
)
