from setuptools import setup

setup(
    name='twisted-enttec',
    version='0.1',
    author='Barney Gale',
    author_email='barney.gale@gmail.com',
    url='https://github.com/barneygale/twisted-enttec',
    license='MIT',
    description='Python/Twisted support for the Enttec DMX USB Pro',
    long_description=open('README.rst').read(),
    py_modules=['twisted_enttec'],
    install_requires=[
        'twisted',
        'pyserial'
    ],
)