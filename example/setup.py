import setuptools

setuptools.setup(
    name='treesitter-example',
    setup_requires=['cffi>=1.0.0'],
    cffi_modules=['build.py:builder'],
)
