from setuptools import setup

setup(
        name='confini',
        version='0.0.4',
        description='Parse, verify and merge all ini files in a single directory',
        author='Louis Holbrook',
        author_email='dev@holbrook.no',
        license='GPL3',
        packages=[
            'confini',
        ],
        scripts = [
            'scripts/parse.py',
            ],
        url='https://holbrook.no',
        )
