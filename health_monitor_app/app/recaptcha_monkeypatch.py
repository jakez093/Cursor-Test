"""
MonkeyPatch for flask_wtf compatibility with newer Flask versions.

This module provides compatibility monkeypatches for flask_wtf when used
with newer versions of Flask that have moved the Markup class.
"""

import sys
import importlib.util

# First check if flask_wtf is installed
try:
    import flask_wtf
    import flask
except ImportError:
    # Not installed, no need to patch
    pass
else:
    # Check if the current Flask version has removed Markup
    if not hasattr(flask, 'Markup'):
        try:
            # Try to import it from markupsafe which is the correct location
            from markupsafe import Markup
            # Monkeypatch flask module
            flask.Markup = Markup
        except ImportError:
            # markupsafe not installed, just create a minimal compatible class
            class Markup(str):
                def __html__(self):
                    return self
            flask.Markup = Markup

# Patch for werkzeug.urls.url_encode
try:
    import werkzeug.urls
    if not hasattr(werkzeug.urls, 'url_encode'):
        # Try to import from the newer location
        from werkzeug.urls import url_encode as _url_encode
        werkzeug.urls.url_encode = _url_encode
except (ImportError, AttributeError):
    # If we can't find it, create a compatible function
    try:
        import werkzeug.urls
        from urllib.parse import urlencode
        
        # Add a compatible function
        werkzeug.urls.url_encode = urlencode
    except (ImportError, AttributeError):
        # Can't patch, will likely cause an error later
        pass

class RecaptchaPatches:
    @staticmethod
    def apply_patches():
        """
        Apply all compatibility patches
        """
        # All patches are now applied at module import time
        pass 