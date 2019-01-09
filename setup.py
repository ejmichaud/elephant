from setuptools import setup

setup(
	name='elephant',
	version=1.3,
	install_requires=[
		'Click'
	],
	author='Eric J. Michaud',
	license='MIT',
	url='https://github.com/ejmichaud/elephant',
	py_modules=['elephant'],
	entry_points={
          'console_scripts': [
              'elephant=elephant:main'
          ]
      },
)