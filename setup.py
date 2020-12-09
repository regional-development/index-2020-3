# -*- coding: utf-8 -*-
""" The setup script"""
from setuptools import find_packages, setup


with open("README.rst") as readme_file:
    readme = readme_file.read()

setup(
    author="Hryhorii Pavlenko",
    author_email="hryhorii.pavlenko@gmail.com",
    name="src",
    version="0.6",
    description="Бібліотека для розрахунку індексу оцінки діяльності ОДА",
    long_description=readme,
    url="https://index-2020-3.readthedocs.io",
    packages=find_packages(),
)
