#!/usr/bin/env pypy-c

from setuptools import setup

setup(name='JitViewer',
      version='0.1',
      description="Viewer for pypy's jit traces",
      author='Maciej Fijalkowski, Antonio Cuni and the PyPy team',
      author_email='fijall@gmail.com',
      url='http://pypy.org',
      packages=['jitviewer'],
      scripts=['bin/jitviewer.py'],
      requires=['flask', 'pygments', 'simplejson'],
      include_package_data=True,
      package_data={'': ['templates/*.html', 'static/*']},
     )
