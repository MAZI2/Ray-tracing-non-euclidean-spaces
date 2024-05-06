# Tukej definiraš sceno, main pol požene renderjanje itd.

from spaces import *
from objects import *
from render import *

#    y
#    |
#    |
#    |
#    |________ x
#   /
#  /
# z

# - u: rotation around y axis
# - v: rotation around x axis
# - w: rotation around z axis

# ------------------ Settings ------------------
# What space are we in?
space = Euclidean()

# Define the scene tuple: (object(position, rotation, color, visible, ... other))
objects = (Sphere((10, 5, 0), (255, 0, 0), True, 2),
           Plane((0, 0, 0), (0, 0, 90), (0, 255, 0), True))

# Define the lights tuple: (light(position, color, visible))
lights = (Light((10, 20, 0), (255, 255, 255), True))

# Define the camera (position, direction, fov, resolution)
camera = Camera((0, 0, 0), (0, 0, 1), 90, (1920, 1080))

# ------------------ Main ------------------

def main():
    # renderer = Renderer(space, objects, lights, camera)
    # image = renderer.render()
    # Show image
    pass

# Run main:
main()