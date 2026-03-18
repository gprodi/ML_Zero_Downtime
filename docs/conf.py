import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "ML Factory"
copyright = "2026, Équipe MLOps"
author = "Tech Lead"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
html_theme = "sphinx_rtd_theme"
