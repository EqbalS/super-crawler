from setuptools import setup
setup(
    name = "super-crawler",
    version = "1.0",
    py_modules = ['main'],
    entry_points = {
        'console_scripts': [
            'super-crawler = main:main'
        ]
    }
)
