import os
import sys

def resource_path(*path_parts):
    """
    Return absolute path to resource, working for dev and for PyInstaller onefile.
    Usage: resource_path('assets', 'sfx', 'arrow_shot.wav')
    """
    bases = []
    if getattr(sys, "frozen", False):
        bases.append(sys._MEIPASS)
    bases.append(os.path.dirname(os.path.dirname(__file__)))

    for base in bases:
        candidate = os.path.join(base, *path_parts)
        if os.path.exists(candidate):
            return candidate

    return os.path.join(bases[0], *path_parts)
