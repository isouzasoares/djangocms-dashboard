#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup

setup(
    name='djangocms-dashboard',
    version='0.0.0',
    description='A dashboard to manage DjangoCMS resources like plugins,'
                'apphooks, etc., in a central interface.',
    long_description=open('README.md', encoding='utf-8').read(),
    author='The Goodfellas',
    author_email='sidnei@thegoodfellas.com.br',
    url='https://bitbucket.org/3mwdigital/djangocms-dashboard',
    # download_url='https://pypi.python.org/pypi/djangocms-dashboard',
    license='BSD 2',
    packages=find_packages(exclude=('tests.*', 'tests', 'example')),
    install_requires=[
        'Django>=1.9.7',
        'unicodecsv>=0.14.0',
    ],
    include_package_data=True,
    #zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD 2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
