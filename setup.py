#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools
from setuptools.command.install import install
import os
import sys
from console_retry.version import VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setuptools.setup(
    name="console_retry",
    version="1.0.2",
    author="Kristofer Borgström",
    description="This utility is designed to run any shell command and retry if no new line was written to"
                "stdout within a specified timeout",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NaturalCycles/console-retry",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": ['console-retry = console_retry.retry:main']
    },
    python_requires='>=3.5',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)