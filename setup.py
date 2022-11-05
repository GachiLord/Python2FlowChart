from setuptools import setup

setup(name='Python2FlowChart',
      version='0.5.1',
      description='CLI-tool translating python to json for block-diagram-redactor site',
      url='',
      author='GachiLord',
      author_email='name50525@gmail.com',
      license='GPL-3.0',
      packages=['Python2FlowChart'],
      install_requires=[],
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'py2fc = Python2FlowChart.__main__:main'
        ]
      }
      )
