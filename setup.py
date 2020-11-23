import setuptools
from setuptools import setup

install_requires = [
		"backports.pbkdf2==0.1",
		"certifi==2020.11.8",
		"cffi==1.14.3",
		"chardet==3.0.4",
		"idna==2.10",
		"pycparser==2.20",
		"PyNaCl==1.4.0",
		"requests==2.25.0",
		"six==1.15.0",
		"urllib3==1.26.2",
		"tenacity",
		"pytest"
	]

classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3 :: Only',
    'Operating System :: POSIX',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries'
]

setup(name='py-skydb',
		version='0.0.1',
		description="A Simple Python Wrapper for using SkyDB",
		classifiers=classifiers,
		author="Powerloom",
		author_email="",
		url="https://github.com/PowerLoom/py-skydb",
		packages=setuptools.find_packages(),
		python_requires = '>=3.6',
		install_requires = install_requires
		)

