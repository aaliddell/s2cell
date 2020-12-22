import pathlib
import re

import setuptools


# Load version
# Cannot import the package at this point, as dependencies are missing
init_file = pathlib.Path(__file__).parent / 's2cell' / '__init__.py'
__version__ = re.search(r"^__version__ = '(.*?)'$", init_file.read_text(), re.MULTILINE).group(1)

# Load readme as long description
with open('README.rst') as file:
    long_description = file.read()

setuptools.setup(
    name='s2cell',
    version=__version__,
    author='Adam Liddell',
    author_email='s2cell@aliddell.com',
    description='Minimal Python S2 cell ID, S2 token and lat/lon conversion library',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://docs.s2cell.aliddell.com',
    download_url="https://pypi.python.org/pypi/s2cell",
    project_urls={
        'Documentation': 'https://docs.s2cell.aliddell.com',
        'Source Code': 'https://github.com/aaliddell/s2cell',
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.15,<2',
    ],
    extras_require={
        'dev': [
            'bandit~=1.7.0',
            'flake8~=3.8',
            'nox~=2020.8.22',
            'pydocstyle~=5.1',
            'pylint~=2.6.0',
            'pytest~=6.2.1',
            'pytest-cov~=2.10',
            'pytest-instafail~=0.4.2',
            'pytest-xdist~=2.2.0',
            'Sphinx~=3.4.0',
            'sphinx-redactor-theme==0.0.1',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
