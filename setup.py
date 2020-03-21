import setuptools

with open('readme.md') as fr:
    long_description = fr.read()

setuptools.setup(
    name='FuzzyLogicToolBox',
    version='0.0.1',
    author='Luferov V.S.',
    author_email='lyferov@yandex.ru',
    description='Fuzzy logic tool box as matlab',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Luferov/FuzzyLogicToolBox',
    packages=setuptools.find_packages(),
    python_requires='>=3.7'
)
