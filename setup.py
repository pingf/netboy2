"""
logcc
-------------

This is the description for that library
"""
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='netboy',
    version='2018.03.16',
    url='https://github.com/pingf/netboy2.git',
    license='BSD',
    author='Jesse MENG',
    author_email='pingf0@gmail.com',
    description='the boy for net',
    long_description=read('README.rst'),
    py_modules=['netboy'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['netboy', 'netboy.asyncio_pycurl', 'netboy.celery', 'netboy.remote', 'netboy.selenium_chrome',
              'netboy.support', 'netboy.util'],
    zip_safe=False,
    package_data={
        # 'bin': ['bin/chromedriver'],
    },
    include_package_data=True,
    platforms='any',
    install_requires=[
        'termcc', 'loader', 'aiohttp', 'aiofiles', 'websockets', 'pony', 'terminaltables', 'logcc', 'celery',
        'inquirer', 'selenium', 'pycurl', 'worker', 'wrap', 'redis'
    ],

    data_files=[
        ('bin', ['bin/chromedriver']),
    ],

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
