from setuptools import setup
from io import open


def read(filename):
	with open(filename, encoding='utf-8') as file:
		return file.read()


setup(
	name='npdtools',
	version='0.1a4',
	packages=['npdtools', 'npdtools.types', 'npdtools.errors'],
	url='https://gitlab.com/whiteapfel/npdtools',
	license='MPL 2.0',
	author='WhiteApfel',
	author_email='white@pfel.ru',
	description='tool for work with FNS API',
	install_requires=['typing', 'httpx'],
	project_urls={
		"Документальное чтиво": "https://npd-tools.readthedocs.io/en/latest/",
		"Донатик": "https://pfel.cc/donate",
		"Исходнички": "https://gitlab.com/whiteapfel/npdtools/",
		"Тележка для вопросов": "https://t.me/apfel"
	},
	long_description=read('README.md'),
	long_description_content_type="text/markdown",
	keywords='FNS API wrapper nalog налог ФНС самозанятость'
)
