
from setuptools import setup, find_packages

setup(
    name='recycling',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'tqdm',
    ],
    author='Deepjyoti',
    author_email='dasd@chalmers.se',
    description='A package for recycling analysis.',
    license='MIT',
    keywords='recycling analysis, vehicle',
)
    