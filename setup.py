#!/usr/bin/env python

from setuptools import setup

setup(
    name='citizens',
    version='0.0.1',
    description='REST API service for yandex backend school',
    long_description='REST API service for yandex backend school',
    author='Dmitrii Dorofeev',
    author_email='d.d0r0feev@yandex.ru',
    url='https://storage.yandexcloud.net/yandex-backend-school/citizens-0.0.1.tar.gz',
    download_url='https://storage.yandexcloud.net/yandex-backend-school/citizens-0.0.1.tar.gz',
    packages=['citizens', 'tests'],
    data_files=[
        ('configs', ['configs/nginx.conf', 'configs/supervisor.conf']),
        ('static', ['static/robots.txt']),
        ('.', ['citizens.config.json', 'install.sh', 'requirements.txt',
               'README.md', 'LICENSE', 'Makefile'])
    ],
    license='MIT',
    platforms=['Ubuntu >= 18.04'],
    install_requires=['aiohttp', 'aiojobs', 'pymongo', 'numpy']
)
