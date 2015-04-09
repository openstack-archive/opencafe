import sphinx_rtd_theme
import sys
import os
import shlex

package_path = os.path.abspath("../../../opencafe")
sys.path.append(package_path)


def remove_module_docstring_license(app, what, name, obj, options, lines):
    license = [
        u'Licensed under the Apache License, Version 2.0 (the "License");',
        u'you may not use this file except in compliance with the License.',
        u'You may obtain a copy of the License at',
        u'',
        u'    http://www.apache.org/licenses/LICENSE-2.0',
        u'',
        u'Unless required by applicable law or agreed to in writing, software',
        u'distributed under the License is distributed on an "AS IS" BASIS,',
        u'WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, \
            either express or implied.',
        u'See the License for the specific language governing permissions and',
        u'limitations under the License.']

    if what == "module":
        if lines[2:13] == license:
            del lines[2:13]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring_license)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'OpenCAFE'
copyright = u'2015, RackspaceQE'

# The short X.Y version.
version = '0.2.0'
# The full version, including alpha/beta/rc tags.
release = '0.2.0'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'monokai'


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
theme_path = sphinx_rtd_theme.get_html_theme_path()
html_theme = "sphinx_rtd_theme"
html_theme_path = [theme_path]

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# Output file base name for HTML help builder.
htmlhelp_basename = 'OpenCAFEdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [('index', 'OpenCAFE.tex', u'OpenCAFE Documentation',
                    u'Rackspace', 'manual')]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'opencafe', u'OpenCAFE Documentation',
     [u'Rackspace'], 1)
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index',
     'OpenCAFE',
     u'OpenCAFE Documentation',
     u'Rackspace',
     'OpenCAFE',
     'One line description of project.',
     'Miscellaneous')]
