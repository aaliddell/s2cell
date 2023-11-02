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
    description='Minimal Python S2 Geometry cell ID, token and lat/lon conversion library',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://docs.s2cell.aliddell.com',
    download_url="https://pypi.python.org/pypi/s2cell",
    project_urls={
        'Documentation': 'https://docs.s2cell.aliddell.com',
        'Source Code': 'https://github.com/aaliddell/s2cell',
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=[],
    extras_require={
        'dev': [
            'flake8~=6.1.0',
            'furo==2023.9.10',
            'nox~=2023.4.22',
            'pydocstyle~=6.3.0',
            'pylint~=3.0.2',
            'pytest~=7.4.3',
            'pytest-cov~=4.1.0',
            'pytest-instafail~=0.5.0',
            'pytest-xdist~=3.3.1',
            'Sphinx~=7.2.6',
            'sphinx-notfound-page~=1.0.0',
            'sphinx-sitemap==2.5.1',
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
