from setuptools import setup, find_packages

setup(
    name='gshock_api',
    version='2.0.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'pytz',
        'bleak',
    ],
    entry_points={
        'console_scripts': [
            'gshock_server=examples.gshock_server:main',
        ],
    },
)
