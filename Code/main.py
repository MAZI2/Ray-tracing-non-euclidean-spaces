# SETUP OD STUFF
import logging
from utilities import suppress_stdout, Logger
Logger.configure("Logs/raytracer.log", logging.DEBUG, False, True)

from objects import Sphere, Plane, Light, Camera
from spaces import Euclidean, FlatTorus, TwoSphere
from scene import Scene
Scene.configure({"sphere": Sphere((3, 0, 0), 1, (255, 0, 255)), 
                 "sphere1": Sphere((1.8, 0.8, 1), 0.2, (0, 255, 255)), 
                 "sphere3": Sphere((1.8, -0.8, -1), 0.2, (0, 255, 255)), 
                 "plane": Plane((0, -2, 0), (0, 1, 0), (255, 100, 0)),
                 "light": Light((0, 3, 3), ), 
                 "camera": Camera((0, 0, 0), (0, 0, 0), (320, 240), 180), # 127 za 90 stopinj levo desno fov
                 "euclidean": Euclidean()})

from ui import _UIThread
_UIThread.configure(4)

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
