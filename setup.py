import setuptools
from brags.version import Version


setuptools.setup(name='brags',
                 version=Version('1.0.0').number,
                 description='Python Package Boilerplate',
                 long_description=open('README.md').read().strip(),
                 author='Package Author',
                 author_email='omkargwagholikar@gmail.com',
                 url='http://path-to-my-packagename',
                 py_modules=['packagename'],
                 install_requires=[],
                 license='MIT License',
                 zip_safe=False,
                 keywords='rag go filewatcher',
                 classifiers=['Packages', 'Boilerplate'])
