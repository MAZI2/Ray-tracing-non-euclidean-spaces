# Tukej definiraš sceno, main pol požene renderjanje itd.
import threading
import queue
import time

from ui import _UIThread
from working import Working




#    y
#    |
#    |
#    |
#    |________ x
#   /
#  /
# z

# Position: (x, y, z
# Rotation: (u, v, w), Default smer je v smeri osi x

# - u: rotation around y axis
# - v: rotation around z axis
# - w: rotation around x axis

# ------------------ Logging ------------------
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# ------------------ Main ------------------

def main():
    working = Working()
    ui_thread = _UIThread()

    # Start terminal thread# ddf
    working.start_thread()

    # Main loop
    ui_thread.ui_loop()

    # Clean up
    working.stop_thread()
    ui_thread.stop()
        
if __name__ == "__main__":
    main()
