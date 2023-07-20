from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='futuram',
      version='0.1',
      description='SRM recovery model for the FutuRaM project',
      url='https://github.com/FutuRaM-Project/IntegratedModel',
      author='FutuRaM',
      author_email='s.c.mcdowall@cml.leidenuniv.nl',
      license='MIT',
      packages=['src.futuram'],
      install_requires=requirements,
      zip_safe=False)