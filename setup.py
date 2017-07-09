from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='reproducibility',
      version='0.1',
      description='Tools for reproducing figures and files required to plot them, such as subsets of large datasets or or derived fields.',
      url='https://github.com/apaloczy/reproducibility',
      license='MIT',
      packages=['reproducibility'],
      install_requires=[
          'matplotlib',
          'datetime',
          'netCDF4',
          'gitpython'
      ],
      test_suite = 'nose.collector',
      zip_safe=False)
