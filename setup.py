import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='footprints_v11',
    version='0.1',
    author='Katlin Sampson',
    author_email='kvsampso@purdue.edu',
    description='Python wraper for footprints v11 web API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.itap.purdue.edu/ITIS-Networking/footprints_v11',
    project_urls={
        'Bug Tracker': 'https://github.itap.purdue.edu/ITIS-Networking/footprints_v11/issues',
    },
    license="LICENSE.md",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=['xmltodict>=0.12.0', ''],
)