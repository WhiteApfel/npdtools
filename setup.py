from io import open
from os import environ

from setuptools import setup


def read(filename):
    with open(filename, encoding="utf-8") as file:
        return file.read()


def requirements():
    with open('requirements.txt', 'r') as req:
        return [r for r in req.read().split("\n") if r]


setup(
    name="npdtools",
    version=environ.get("CI_COMMIT_TAG", '0.0.1local').replace('v', ''),
    packages=["npdtools", "npdtools.types"],
    url="https://gitlab.com/whiteapfel/npdtools",
    license="MPL 2.0",
    author="WhiteApfel",
    author_email="white@pfel.ru",
    description="tool for work with FNS API",
    install_requires=requirements(),
    project_urls={
        "Документация": "https://npd-tools.readthedocs.io/en/latest/",
        "Исходники": "https://gitlab.com/whiteapfel/npdtools/",
        "По вопросам": "https://t.me/apfel",
    },
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords="FNS API wrapper nalog налог ФНС самозанятость",
)
