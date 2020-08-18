from setuptools import setup

setup(
        name='confini',
        version='0.0.1',
        description='Parse, verify and merge all ini files in a single directory',
        author='Louis Holbrook',
        author_email='dev@holbrook.no',
        packages=[
            'confini',
        ],
        scripts = [
            'scripts/parse.py',
            ],
        data_files = [('', ['LICENSE.txt'])],
        url='https://holbrook.no',
        )
