# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add repository root (for package imports)
sys.path.insert(0, os.path.abspath("../.."))

# Add local Sphinx extensions
sys.path.insert(0, os.path.abspath("_ext"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "SegnoMMS"
copyright = "2025, SYSTMMS"
author = "SYSTMMS"
# Keep Sphinx release in sync with the package version
try:
    import segnomms

    release = getattr(segnomms, "__version__", "0.0.0")
except Exception:
    # Fallback if import fails in doc build environment
    release = "0.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "myst_parser",
    # Auto-generated visual gallery from test baselines
    "visual_gallery",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}
autodoc_typehints = "description"
autodoc_typehints_format = "short"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "segno": ("https://segno.readthedocs.io/en/latest/", None),
}

# Autosummary settings
autosummary_generate = True

# MyST-Parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3

# --- Strict mode for CI only -------------------------------------------------
# Enable nitpicky (treat all missing references as warnings) in CI to catch
# broken cross-references early, but keep it off on Read the Docs to avoid
# noisy builds.
ON_RTD = os.environ.get("READTHEDOCS") == "True"
ON_CI = bool(os.environ.get("CI"))
# Allow explicit override via SPHINX_STRICT=1
STRICT_OVERRIDE = os.environ.get("SPHINX_STRICT") in {"1", "true", "True"}

nitpicky = (ON_CI or STRICT_OVERRIDE) and not ON_RTD

# Common, harmless references that don't need to resolve
nitpick_ignore = [
    ("py:class", "typing.Any"),
    ("py:class", "typing.Optional"),
    ("py:class", "typing.Dict"),
    ("py:class", "typing.List"),
    ("py:class", "typing.Tuple"),
    ("py:class", "ET.Element"),
    ("py:class", "xml.etree.ElementTree.Element"),
    ("py:class", "pydantic.main.BaseModel"),
]

# Ignore noisy annotated type references and constraint shorthands
nitpick_ignore_regex = [
    (r"py:.*", r"annotated_types\\..*"),
    (r"py:class", r".*=.*"),  # e.g., ge=0, gt=0
    (r"py:class", r"pydantic_core\\..*"),
    (r"py:class", r"segnomms\\.core\\.models\\..*"),
    (r"py:class", r"segnomms\\.validation\\.models\\..*"),
    (r"py:class", r"tests\\.helpers\\..*"),
]
