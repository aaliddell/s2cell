# -- Project information -----------------------------------------------------

import s2cell
project = 's2cell'
copyright = '2020, Adam Liddell - Apache 2.0 License'
author = 'Adam Liddell'
release = s2cell.__version__
version = release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['.ipynb_checkpoints']

# Code highlighting
pygments_style = 'default'

# Enable figure numbering
numfig = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_redactor_theme
html_theme = 'sphinx_redactor_theme'
html_theme_path = [sphinx_redactor_theme.get_html_theme_path()]

# Logo and favicon
html_logo = 'source/_static/logo.min.svg'
html_favicon = 'source/_static/logo-64.png'

# Base URL for docs
# Used to generate CNAME file
html_baseurl = 'https://docs.s2cell.aliddell.com'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['source/_static']

# Theme options
html_theme_options = {
    'display_version': True,
}

# Disable footer
html_show_sphinx = False

# Template overrides
templates_path = ['_templates']

# Add CSS files
html_css_files = [
    'pygments.css',  # Manually add pygments.css, since sphinx_redactor_theme does not
    'customise.css',
]


# -- Options for autodoc -----------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': True,
}
