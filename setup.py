# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pip-license-checker",
    version="0.1.0",
    py_modules=["pip_license_checker"],
    entry_points={
        "console_scripts": [
            "pip=pip_license_checker:main",
        ],
    },
    install_requires=[
        "pip>=20.0.0",
    ],
    description="A pip extension that checks package licenses before installation",
    long_description=long_description,
    long_description_content_type="text/markdown",

)