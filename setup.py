import os
import re
import setuptools

NAME = "pymerger"
AUTHOR = "yyaammeennkk"
AUTHOR_EMAIL = "yyaammeennkk@gmail.com"
DESCRIPTION = "Python, MicroPython and CircuitPython files merger"
LICENSE = "MIT"
KEYWORDS = "merger files"
URL = "https://github.com/yamenk-gribaudo/" + NAME
README = ".github/README.md"
CLASSIFIERS = [
    "Topic :: Text Processing :: General",
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",

]
INSTALL_REQUIRES = [
    "astunparse",
    "ast_scope"
]
ENTRY_POINTS = {

}
SCRIPTS = [

]

HERE = os.path.dirname(__file__)


def read(file):
    with open(os.path.join(HERE, file), "r") as fh:
        return fh.read()


VERSION = re.search(
    r'__version__ = [\'"]([^\'"]*)[\'"]',
    read(NAME.replace("-", "_") + "/__init__.py")
).group(1)

LONG_DESCRIPTION = read(README)

if __name__ == "__main__":
    setuptools.setup(
        name=NAME,
        version=VERSION,
        packages=setuptools.find_packages(),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        license=LICENSE,
        keywords=KEYWORDS,
        url=URL,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        scripts=SCRIPTS,
        include_package_data=True
    )
