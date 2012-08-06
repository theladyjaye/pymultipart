#!/usr/bin/env python
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

packages = [
    'pymultipart'
]

setup(
    name='pymultipart',
    version='0.1',
    description='HTTP Multipart Body Parser',
    long_description=readme,
    author='Adam Venturella',
    author_email='aventurella@gmail.com',
    url='https://github.com/aventurella/pymultipart',
    license=license,
    packages=packages,
    package_data={'': ['LICENSE']},
    platforms=['Any'],
    scripts=[],
    provides=[],
    namespace_packages=[],
    include_package_data=True,
    package_dir={'pymultipart': 'pymultipart'},

    zip_safe=False,
)
