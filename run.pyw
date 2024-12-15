import os
import sys

import server
import update

update.main()

python = sys.executable
os.execl(python, python, server.__file__)
