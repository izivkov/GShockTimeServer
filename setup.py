"""
    Setup file for GShockTimeServer.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.4.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup, find_packages

setup(
    name='gshock-api',
    version='0.9',
    use_scm_version=True,
    packages=find_packages(),
    install_requires=[
        'pytz', 'bleak', 'reactivex', 'args'
    ],

    author='Ivo Zivkov',
        author_email='izivkov@gmail.com',
        description='This library allows you to interact with your G-Shock watch from Python',
        long_description='This library allows you to interact with your G-Shock watch from Python...',
        url='https://github.com/izivkov/GShockTimeServer',
        license='MIT',  # Choose an appropriate license
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
)
