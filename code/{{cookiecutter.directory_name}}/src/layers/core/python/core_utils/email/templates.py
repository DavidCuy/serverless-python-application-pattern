"""
This module provides utilities for handling email templates.
Functions:
    read_template(template_path: str) -> str:
        Reads and returns the contents of a template file specified by the given path.
Constants:
    TEMPLATE_PATH (Path): The directory path where email templates are stored.
    TEMPLATE_CONFIG (dict): Configuration dictionary for email templates, including file paths,
        email subjects, required variables, and the template content.
"""

from pathlib import Path
from enum import Enum

def read_template(template_path: str) -> str:
    """
    Reads the contents of a file specified by the given template path.

    Args:
        template_path (str): The path to the template file to be read.

    Returns:
        str: The contents of the template file as a string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        IOError: If an I/O error occurs while reading the file.
    """
    with open(template_path, 'r') as f:
        content = f.read()
        return content

TEMPLATE_PATH = Path(__file__).parent

class TemplateNames(Enum):
    EXAMPLE = "template-name"

TEMPLATE_CONFIG = {
    TemplateNames.EXAMPLE: {
        'path': TEMPLATE_PATH / 'example_template.html',
        'subject': 'Example',
        'variables': ['EXAMPLE'],
        'content': read_template((TEMPLATE_PATH / 'example_template.html').resolve()),
    }
}
