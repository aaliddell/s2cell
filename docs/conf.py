import datetime
import os

# -- Project information -----------------------------------------------------

import s2cell
project = 's2cell'
copyright = '2020-{}, Adam Liddell - Apache 2.0 License'.format(
    datetime.date.today().year
)
author = 'Adam Liddell'
release = s2cell.__version__
version = release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Internal
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',

    # External
    'notfound.extension',
    'sphinx_sitemap',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['.ipynb_checkpoints', '**/.ipynb_checkpoints', 'api/s2cell.rst']

# Code highlighting
pygments_style = 'monokai'

# Enable figure numbering
numfig = True

# Setup root doc
root_doc = 'index'


# -- Run sphinx-apidoc -------------------------------------------------------

def run_apidoc(_):
    import sphinx.ext.apidoc

    docs_path = os.path.dirname(__file__)
    apidoc_path = os.path.join(docs_path, 'api')
    module_path = os.path.join(docs_path, '..', 's2cell')

    sphinx.ext.apidoc.main([
        '--no-toc',
        '--force',
        '--separate',
        '-o', apidoc_path,
        module_path
    ])


def setup(app):
    app.connect('builder-inited', run_apidoc)


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

# Title
html_title = 's2cell'

# Logo and favicon
html_logo = 'static/logo.min.svg'
html_favicon = 'static/logo-64.png'

# Base URL for docs
# Used to generate CNAME file
html_baseurl = 'https://docs.s2cell.aliddell.com'

# Extra vars to provide to templating
html_context = {
    'baseurl': html_baseurl,
    'icon_png': 'logo.png'
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']

# Theme options
html_theme_options = {
    'sidebar_hide_name': True,
    'light_css_variables': {
        'color-brand-primary': '#de6b00',
        'color-brand-content': '#de6b00',
    },
    'dark_css_variables': {
        'color-brand-primary': '#de6b00',
        'color-brand-content': '#de6b00',
    },
}

# Disable footer
html_show_sphinx = False

# Add CSS files
html_css_files = []

# Extra files to include
html_extra_path = [
    'robots.txt',
]

# Sitemap options
sitemap_filename = "sitemap-override.xml"  # RTD generates sitemap with not much in it...
sitemap_url_scheme = "{link}"

# -- Options for autodoc -----------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    #'special-members': '__init__',
    #'undoc-members': True,
    'show-inheritance': True,
    #'inherited-members': True,
}
