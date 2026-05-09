# Configuration file for the Sphinx documentation builder.

try:
    import hftbacktest
except Exception:
    hftbacktest = None

project = "hftbacktest 中文文档"
copyright = "2024, nkaz001; Chinese translation contributors"
author = "nkaz001; Chinese translation contributors"
release = hftbacktest.__version__ if hftbacktest is not None else ""

extensions = [
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.jquery",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "zh_CN"
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = "hftbacktest 中文文档"

add_module_names = False
autosummary_generate = True
autodoc_typehints = "description"
autodoc_mock_imports = ["databento"]
keep_warnings = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.10/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "numba": ("https://numba.readthedocs.io/en/stable/", None),
    "polars": ("https://docs.pola.rs/api/python/stable/", None),
}
