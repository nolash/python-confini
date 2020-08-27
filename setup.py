from setuptools import setup

setup(
        name='confini',
        version='0.1.0',
        description='Parse, verify and merge all ini files in a single directory',
        author='Louis Holbrook',
        author_email='dev@holbrook.no',
        license='GPL3',
        install_requires=[
            'python-gnupg>=0.4.6,<0.5.0',
        ],
        scripts = [
            'scripts/parse.py',
            ],
        url='https://holbrook.no',
        )
