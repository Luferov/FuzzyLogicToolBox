import setuptools
import fuzzy_logic

with open('readme.md') as fr:
    long_description = fr.read()

setuptools.setup(
    name='fuzzy_logic_toolbox',
    version=fuzzy_logic.__version__,
    author='Luferov V.S.',
    author_email='lyferov@yandex.ru',
    description='Fuzzy logic tool box as matlab',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Luferov/FuzzyLogicToolBox',
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy>=1.18.2'
    ],
    test_suite='tests',
    python_requires='>=3.7',
    platforms=["any"]
)
