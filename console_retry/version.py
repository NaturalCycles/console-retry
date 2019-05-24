"""
circleci.version
~~~~~~~~~~~~~~~~
    This module provides some helper functions to set version in various places.
    .. versionadded:: 1.2.0
"""
VERSION = "1.0.2"
"""Current version of console-retry util."""

def get_short_version():
    """
    Format "short" version in the form of X.Y
    :returns: short version
    """
    ver = VERSION.split(".")
    short_version = "{0}.{1}".format(ver[0], ver[1])
    return short_version