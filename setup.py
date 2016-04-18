try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='urlshortener',
      version='1.1.3',
      py_modules=['main'])
