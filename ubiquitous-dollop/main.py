from os import system, path
from sys import platform

from src import *

if __name__ == "__main__":
    module_dir, _ = path.split(__file__)
    module_dir = module_dir.replace("\\", "/")
    if "win" in platform.lower():
        system(f"set PATH=%PATH%;{module_dir}")
    else:
        system(f"export PYTHONPATH={module_dir}:$PYTHONPATH")

    app = App()
    app.start()
