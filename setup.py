#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages


setup(name='PyFL593FL',
      version='0.0.1',
      author='Ronny Eichler',
      author_email='ronny.eichler@gmail.com',
      url='https://github.com/wonkoderverstaendige/PyFL593FL',
      download_url='https://github.com/wonkoderverstaendige/PyFL593FL',
      description='Python interface to the Team Wavelength FL593FL laser diode driver evaluation board',
      long_description='Python interface to the Team Wavelength FL593FL laser diode driver evaluation board',

      packages = find_packages(),
      include_package_data = True,
      package_data = {
        '': ['*.txt', '*.rst'],
        'PyFL593FL': ['data/*.html', 'data/*.css'],
      },
      exclude_package_data = { '': ['README.md'] },
      
      scripts = ['bin/my_program'],
      
      keywords='hardware serial laser-diode driver',
      license='MIT',
      classifiers=['Development Status :: 3 - Alpha',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
                  ],
                  
      #setup_requires = ['python-stdeb', 'fakeroot', 'python-all'],
      install_requires = ['setuptools', 'pyserial', 'PyUSB'],
      extra_requires = {
          'gui': ['PyQt4'],
     )

