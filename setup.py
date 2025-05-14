#!/usr/bin/env python3
"""
Lutron Telnet Controller - Setup file
"""
from setuptools import setup, find_packages

setup(
    name="lutron-telnet",
    version="1.0.0",
    description="Lutron Caseta Smart Bridge Pro controller via Telnet",
    author="Val",
    packages=find_packages(),
    scripts=["lutron_cli.py"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Home Automation",
    ],
) 