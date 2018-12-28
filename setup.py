import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='treesitter',
    version='0.0.1',
    author='George Hopkins',
    author_email='george-hopkins@null.net',
    description='Python bindings for tree-sitter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/george-hopkins/python-tree-sitter',
    packages=setuptools.find_packages(),
    setup_requires=['cffi>=1.0.0'],
    cffi_modules=['treesitter/build.py:runtime_builder'],
    install_requires=['cffi>=1.0.0'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    include_package_data=True,
)
