from setuptools import setup

setup(
    name="cautious_sniffle",
    version="0.0.1",
    description="A Python Non Linear Solver",
    url="https://github.com/araujo-fernando/cautious-sniffle",
    author="Fernando Araujo",
    author_email="flaraujojunior@gmail.com",
    license="",
    packages=["solver"],
    install_requires=[
        "numpy",
        "tqdm",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.9",
    ],
)
