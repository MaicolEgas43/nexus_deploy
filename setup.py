from setuptools import setup, find_packages

setup(
    name='mi_lib',
    version='0.1.0',
    author='Maicol Egas',
    author_email='maicolegas43@gmail.com',
    description='Una libreria de ejemplo para subir a nexus',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.10',
)