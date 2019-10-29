from setuptools import setup

install_requires = [
    'pandas',
]

setup(
    name='data_tools',
    author='Mike Mayers',
    author_email='mmayers@scripps.edu',
    url='https://github.com/mmayers12/data_tools',
    version='0.0.1',
    packages=['data_tools'],
    license='LICENSE',
    description='Tools for manipulating data, particularly with the end goal of forming hetnet',
    long_description=open('README.md').read(),
    install_requires=install_requires,
    python_requires='>=3.6',
)
