from setuptools import setup

VERSION = "0.1.0"  # PEP-440

# read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# read dependency requirements
with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

setup(
    name="composr",
    version=VERSION,
    description="Static report generator",
    author="Asif Rahman",
    author_email="asiftr@gmail.com",
    url="https://github.com/asifr/composr",
    license="MIT",
    packages=["composr"],
    install_requires=install_requires,
    keywords=["documentation"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
