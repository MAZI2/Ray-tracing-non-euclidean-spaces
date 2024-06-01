# SETUP OD STUFF
import logging
from utilities import suppress_stdout, Logger
Logger.configure("Logs/raytracer.log", logging.DEBUG, False, True)

from objects import Sphere, Plane, Light, Camera
from spaces import Euclidean, FlatTorus, TwoSphere
from scene import Scene
Scene.configure({"sphere": Sphere((7, 0, 0), 2, (255, 145, 71)), 
                  "sphere1": Sphere((4.3, 1.6, 2), 0.5, (79, 158, 245)), 
                  "sphere2": Sphere((6.7, -2.3, -3), 0.5, (198, 91, 124)), 
                  "plane": Plane((0, -3, 0), (0, 1, 0), (200, 200, 200)),
                  "light": Light((0, 6, 8)), 
                  # "camera": Camera((0, 0, 0), (0, 0, 0), (1600, 1200), 170), # 127 za 90 stopinj levo desno fov
                  "camera": Camera((-4, 2, 0), (0, 0, 0), (1400, 1000), 84), # 127 za 90 stopinj levo desno fov
                  "twosphere": TwoSphere(13)})

from ui import _UIThread
_UIThread.configure(1)

# IMPORTS
from working import Working
# Suppress pygame initialization message
with suppress_stdout():
    import pygame


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

# ------------------ Main ------------------

def main():
    working = Working()
    ui_thread = _UIThread()

    # Start terminal thread 
    working.start_thread()

    # Main loop ish (main thread je za UI)
    ui_thread.ui_loop()

    # Clean up
    working.stop_thread()
    ui_thread.stop()
        
if __name__ == "__main__":
    main()
