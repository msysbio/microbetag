from setuptools import setup, find_packages


# Read the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='microbetag',
    version='1.0.3',
    description='Setting up a python package',
    author='Haris Zafeiropoulos',
    author_email='haris.zafeiropoulos@kuleuven.be',
    url='https://hariszaf.github.io',
    packages=find_packages(include=['microbetag', 'microbetag.*']),
    include_package_data=True,
    package_data={
        'microbetag': [
            'microbetagDB/mappings/*',
            'microbetagDB/ref-dbs/*',
            'microbetagDB/ref-dbs/phenDB/predictions/*'
        ]
    },
    install_requires=requirements,
    extras_require={'plotting': ['matplotlib>=2.2.0']},
)


# python setup.py  sdist bdist_wheel
# pip install .