#from setuptools import setup, find_packages
from setuptools import find_packages
from distutils.core import setup, Extension


def main():
    setup(name="matlab_gym",
          version="0.0.1",
          packages=[package for package in find_packages()],
          ext_modules=[Extension("fastwait", ["fastwait.c"])]
          )
          
if __name__ == "__main__":
    main()

