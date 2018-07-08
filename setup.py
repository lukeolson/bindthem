#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bindthem.py

A simple script for c++ kernels, to find them all and in the darkness bind them (using pybind11).

"""

import os
import sys
import subprocess

import setuptools
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.

    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    #if sys.platform == 'darwin':
    #    c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        try:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        except (AttributeError, ValueError):
            pass
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

    # identify extension modules
    # since numpy is needed (for the path), need to bootstrap the setup
    # http://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py
    def finalize_options(self):
        build_ext.finalize_options(self)
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [Extension('tests.bind_examples',
                         sources=['tests/bind_examples_bind.cpp'],
                         include_dirs=[get_pybind_include(), get_pybind_include(user=True)],
                         language='c++')]

setup(
    name='bindthem',
    version='0.1.0',
    keywords=['C++ Pybind11 Python'],
    author='Luke Olson',
    author_email='luke.olson@gmail.com',
    maintainer='Luke Olson',
    maintainer_email='luke.olson@gmail.com',
    url='https://github.com/lukeolson/bindthem',
    license='MIT',
    platforms=['Windows', 'Linux', 'Solaris', 'Mac OS-X', 'Unix'],
    description=__doc__.split('\n')[0],
    long_description=__doc__,
    #
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    #
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExt, 'test': PyTest},
    install_requires = ['numpy>=1.7.0', 'pytest>=2', 'pybind11>=2.2',
                        'pyyaml', 'CppHeaderParser'],
    setup_requires=['numpy', 'pybind11'],
    tests_require=['pytest'],
    #
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    scripts=['bindthem.py'],
)
