import os
from setuptools import setup, find_packages

__all__ = ["setup"]


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ""


def get_readme():
    """Return the README file contents. Supports text,rst, and markdown"""
    for name in ("README", "README.rst", "README.md"):
        if os.path.exists(name):
            return read_file(name)
    return ""


def install_requires():
    requirements = read_file("requirements.txt")
    return requirements


setup(
    name="live_client",
    version="0.5.2",
    description="Client libraries to connect with the Intelie LIVE platform",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    scripts=["live_client/scripts/check_live_features"],
    url="https://github.com/intelie/liveclient-python",
    author="Vitor Mazzi",
    author_email="vitor.mazzi@intelie.com.br",
    license="Apache",
    install_requires=install_requires(),
    zip_safe=True,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Monitoring",
    ],
)
