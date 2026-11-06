import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # cuando es .exe
    except Exception:
        base_path = os.path.abspath(".")  # cuando es normal

    return os.path.join(base_path, relative_path)