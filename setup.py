from setuptools import setup, find_packages

setup(
    name='gshock_api',
    version='2.0.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'pytz',
        'bleak',
        'reactivex',
    ],
    entry_points={
        'console_scripts': [
            'gshock_server=examples.gshock_server:main',
        ],
    },
    author="Ivo Zivkov",
    author_email="your-email@example.com",
    description="A Python library for interacting with G-Shock watches via BLE.",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url="https://github.com/yourusername/gshock_api",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)