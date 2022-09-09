from setuptools import find_packages, setup


setup(
    name='transaqpy',
    packages=find_packages(),
    version='0.1.0',
    description='Transaq connector integration for python',
    author='Andrey Tkachenko',
    author_email='falko.lab@gmail.com',
    license='MIT',
    install_requires=['protobuf', 'grpcio', 'eulxml',],
    setup_requires=['pytest-runner', 'grpcio-tools'],
    tests_require=['pytest'],
    test_suite='tests',
)
