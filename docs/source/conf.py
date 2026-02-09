"""Sphinx configuration for happygene documentation."""
import os
import sys

# Add the project root to sys.path so Sphinx can find the happygene module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Project information
project = 'happygene'
copyright = '2026, Eric Mumford'
author = 'Eric Mumford'
release = '0.1.0'

# Sphinx extensions
extensions = [
    'sphinx.ext.autodoc',      # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',     # Support for Google and NumPy docstring styles
    'myst_parser',             # Support for Markdown (.md) files
    'sphinx.ext.viewcode',     # Link to source code
]

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Master document
master_doc = 'index'

# Theme
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
}

# HTML output options
html_static_path = []
html_css_files = []

# Autodoc options
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True,
}

# Napoleon options (for NumPy/Google style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# MyST parser options
myst_enable_extensions = [
    'colon_fence',
    'fieldlist',
]

# Suppress warnings for missing references
suppress_warnings = ['myst.ref_not_found']

# Exclude patterns
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
]

# Pygments theme for syntax highlighting
pygments_style = 'sphinx'

# Language
language = 'en'

# Locale for date
today_fmt = '%Y-%m-%d'

# Relative URLs
html_use_opensearch = ''
html_file_suffix = '.html'
