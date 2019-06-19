try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pytravelcard',
    version='0.1',
    description='tools for interacting with ITSO-compliant smartcards',
    url='https://github.com/unlobito/pytravelcard',
    author='Harley Watson',
    author_email="htw@lobi.to",
    license='GNU General Public License v2 (GPLv2)',
    packages=['pytravelcard'],
    entry_points={
        'console_scripts': [
            'pytravelcard = pytravelcard.cli:cli'
        ]
    },
    cffi_modules=["pytravelcard.libfreefare_build:ffibuilder"],
    install_requires=[
        'click',
        'cffi',
        'bitstring'
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
)
