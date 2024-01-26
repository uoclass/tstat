"""Start Python module search at project root"""

import sys, os
this_folder = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(this_folder, "..")))