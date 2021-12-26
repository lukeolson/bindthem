#!/usr/bin/env python
"""
bindthem: A simple script for C++ kernels,
to find them all and in the darkness bind them.

The C++ kernels are very limited.  Uses pybind11.
"""

from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [Pybind11Extension('tests.bind_examples',
                                  sources=['tests/bind_examples_bind.cpp'],
                                )]

setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    scripts=['bindthem.py'],
)
