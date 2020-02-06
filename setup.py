from setuptools import setup

setup(
    name='live_client',
    version='0.0.1',
    description='Client libraries to connect with the Intelie LIVE platform',
    url='https://github.com/intelie/liveclient-python',
    author='Vitor Mazzi',
    author_email='vitor.mazzi@intelie.com.br',
    license='Apache',
    packages=['live_client'],
    install_requires=[
        'aiocometd==0.4.5',
        'eliot==1.10.0',
        'eliot-tree==18.1.1',
        'pytz==2019.2',
        'requests==2.22.0',
        'setproctitle==1.1.10',
    ],
    zip_safe=False
)
