# Tukej definiraš sceno, main pol požene renderjanje itd.
from spaces import *
from objects import *
from render import *
from scene import *

import logging
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
# - v: rotation around x axis
# - w: rotation around z axis

# ------------------ Main ------------------

def main():
    scene = Scene(Euclidean(), [Plane("plane", (10, 0, 0))], Light("light", (10, 10, 0), ), Camera("camera", (0, 0, 0), (0, 0, 0)))
    
    renderer = Renderer(scene)
    renderer.render()

    running = True


# Run main:
main()
