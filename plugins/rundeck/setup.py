from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-rundeck",
    version=version,
    description='Alerta plugin for rundeck',
    url='https://github.com/alerta/alerta-contrib',
    license='MIT',
    author='Matthieu Serrepuy',
    author_email='matthieu@serrepuy.fr',
    packages=find_packages(),
    py_modules=['alerta_rundeck'],
    install_requires=[
        'requests'
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'rundeck = alerta_rundeck:ServiceIntegration'
        ]
    }
)
