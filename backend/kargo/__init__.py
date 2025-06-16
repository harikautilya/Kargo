import site
import os

def rel(*paths):
    """
    Get absolute path of the file and adds additional paths as need.
    Provides path in linux format
    :rtype: str
    """
    calling_file_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(calling_file_dir)
    relative_path = os.path.join(parent_dir,  *paths)
    return os.path.abspath(relative_path).replace("\\", "/")

# Install each packages depending on the requirements

site.addpackage(rel() , "apps.pth", known_paths=set())
