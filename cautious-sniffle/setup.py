from distutils.core import setup
from setuptools import setup

setup(
    name="cautious_sniffle",
    version="0.0.1",
    description="A Python Non Linear Solver",
    url="https://github.com/araujo-fernando/pubmono/cautious-sniffle",
    author="Fernando Araujo",
    author_email="flaraujojunior@gmail.com",
    license="",
    packages=["solver"],
    install_requires=[
        "numpy",
        "tqdm",
        "seaborn",
        "matplotlib",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.11",
    ],
)
