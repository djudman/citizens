#!/usr/bin/env python

from setuptools import setup

version = '0.1'
download_url = f'https://storage.yandexcloud.net/yandex-backend-school/citizens-{version}.tar.gz'

setup(
    name='citizens',
    version=version,
    description='REST API service for Yandex backend school',
    long_description='A task for joining Yandex backend school (autumn 2019)',
    author='Dmitrii Dorofeev',
    author_email='d.d0r0feev@yandex.ru',
    url=download_url,
    download_url=download_url,
    packages=['citizens', 'tests'],
    data_files=[
        ('configs', ['configs/nginx.conf', 'configs/supervisor.conf']),
        ('static', ['static/robots.txt']),
        ('.', ['citizens.config.json', 'install.sh', 'requirements.txt',
               'README.md', 'LICENSE', 'Makefile', 'Dockerfile', 'entrypoint.sh',
               'run-with-docker.sh'])
    ],
    license='MIT',
    platforms=['Ubuntu >= 18.04'],
    install_requires=['aiohttp', 'aiojobs', 'pymongo', 'numpy']
)
