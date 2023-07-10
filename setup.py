from io import open

from setuptools import setup


def read(filename):
    with open(filename, encoding="utf-8") as file:
        return file.read()


setup(
    name="npdtools",
    version="1.0a2",
    packages=["npdtools", "npdtools.types"],
    url="https://gitlab.com/whiteapfel/npdtools",
    license="MPL 2.0",
    author="WhiteApfel",
    author_email="white@pfel.ru",
    description="tool for work with FNS API",
    install_requires=["typing", "httpx", "python-dateutil", "pydantic>=2.0.2"],
    project_urls={
        "Документация": "https://npd-tools.readthedocs.io/en/latest/",
        "Исходники": "https://gitlab.com/whiteapfel/npdtools/",
        "По вопросам": "https://t.me/apfel",
    },
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords="FNS API wrapper nalog налог ФНС самозанятость",
)
