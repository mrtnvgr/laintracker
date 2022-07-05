#!/bin/python
from setuptools import setup


setup(name="laintracker",
        version="0.0.1-dev",
        license="MIT",
        url="https://github.com/mrtnvgr/laintracker",
        packages=['laintracker'],
        entry_points={'console_scripts': ['lain=laintracker.__main__:main']},
      )
