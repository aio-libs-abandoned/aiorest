import os
import re
import sys
from setuptools import setup, find_packages

install_requires = ['aiohttp>=0.12']

PY_VER = sys.version_info

if PY_VER >= (3, 4):
    pass
elif PY_VER >= (3, 3):
    install_requires.append('asyncio')
else:
    raise RuntimeError("aiorest doesn't suppport Python earllier than 3.3")

extras_require = {'redis_session': ['aioredis>=0.1.3']}


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__), 'aiorest', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        else:
            raise RuntimeError('Cannot find version in aiorest/__init__.py')


classifiers = [
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: OS Independent',
    'Environment :: Web Environment',
]


setup(name='aiorest',
      version=read_version(),
      description=('Support REST calls for asyncio+aiohttp.'),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=classifiers,
      platforms=['OS Independent'],
      author='Andrew Svetlov',
      author_email='andrew.svetlov@gmail.com',
      url='http://aiorest.readthedocs.org',
      download_url='https://pypi.python.org/pypi/aiorest',
      license='BSD',
      packages=find_packages(),
      install_requires=install_requires,
      extras_require=extras_require,
      # tests_require = tests_require,
      # test_suite = 'nose.collector',
      provides=['aiorest'],
      requires=['aiohttp'],
      include_package_data=True)
