from setuptools import setup

setup(
        name='confini',
        version='0.2.0',
        description='Parse, verify and merge all ini files in a single directory',
        author='Louis Holbrook',
        author_email='dev@holbrook.no',
        license='GPL3',
        install_requires=[
            'python-gnupg>=0.4.6,<0.5.0',
        ],
        packages=[
            'confini',
        ],
        scripts = [
            'scripts/parse.py',
            ],
        url='https://holbrook.no',
        )
