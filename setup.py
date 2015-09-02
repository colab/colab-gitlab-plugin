#!/usr/bin/env python
"""
colab-gitlab plugin
===================

A Gitlab plugin for Colab.
"""
from setuptools import setup, find_packages

install_requires = [
    'colab',
    'python-dateutil>=1.5',
    'requests>=2.7.0',
]

tests_require = ['mock']


setup(
    name="colab-gitlab",
    version='0.1.0',
    author='Sergio Oliveira',
    author_email='sergio@tracy.com.br',
    url='https://github.com/colab/colab-gitlab-plugin',
    description='A Gitlab plugin for Colab',
    long_description=__doc__,
    license='GPLv3',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    test_suite="tests.runtests.run",
    tests_require=tests_require,
    extras_require={'test': tests_require},
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
