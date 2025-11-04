"""Test version information."""
import re

from flowrules import __version__


def test_version_format():
    """Test that the version string follows semantic versioning."""
    assert re.match(r"^\d+\.\d+\.\d+$", __version__)


def test_version_import():
    """Test that version is available on the package."""
    assert hasattr(__version__, "__version__")
    assert isinstance(__version__, str)