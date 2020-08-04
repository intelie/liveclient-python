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


setup(
    name="live_client",
    version="0.8.2",
    description="Client libraries to connect with the Intelie LIVE platform",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    scripts=["live_client/scripts/check-live-features"],
    url="https://github.com/intelie/liveclient-python",
    author="Vitor Mazzi",
    author_email="vitor.mazzi@intelie.com.br",
    install_requires=[
        "aiocometd>=0.4.5",
        "eliot>1",
        "eliot-tree",
        "pytz>=2019.2",
        "requests>=2,<3",
        "setproctitle>=1.1.10",
    ],
    zip_safe=True,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Monitoring",
    ],
)
