import re
from setuptools import setup, find_packages

version = ""

requirements = []
# I actually took it from requests library
with open('by_isp_coverage/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

if not version:
    raise ValueError("No version specified.")

setup(
    name="by_isp_coverage",
    version=version,
    description=("Set of class and utilities to parse"
                 "high-speed internet access coverage",
                 "in Minsk and in Belarus in general")[0],
    url='https://github.com/MrLokans/isp-coverage-map/',
    download_url='https://github.com/MrLokans/isp-coverage-map/tarball/{}'.format(version),
    author='MrLokans',
    author_email='mrlokans@gmail.com',
    license='MIT',
    packages=find_packages(exclude=["tests"]),
    entry_points={
        'console_scripts': [
            'isp_coverage = by_isp_coverage.main:main'
        ]
    },
    install_requires=requirements,
    classifiers=(
        'Intended Audience :: Developers, Data Scientists',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
    zip_safe=False
)
