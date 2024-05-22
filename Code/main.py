# Tukej definiraš sceno, main pol požene renderjanje itd.
from spaces import *
from objects import *
from render import *
from scene import *




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
    # Setup stuff
    scene = Scene(Euclidean(), {"plane": Plane("plane", (10, 0, 0)), "light": Light("light", (10, 10, 0), ), "camera": Camera("camera", (0, 0, 0), (0, 0, 0))})
    renderer = Renderer(scene, (20, 10))

    # DEBUG:
    # scene.move(name="light")
    # exit()
    # END DEBUG
    
    while True:
        print()
        line = input("Raytracer>  ")
        if not line:
            continue

        tokens = line.split(" ")
        command = tokens[0]
        if len(tokens) > 1:
            kwargs = parse_kwargs(tokens[1:])
            kwargs["name"] = tokens[1]
        else:
            kwargs = {}

        if command == "quit":
            break
        elif command == "list":
            scene.list()
        elif command == "add":
            scene.add(**kwargs)
        elif command == "remove":
            scene.remove(**kwargs)
        elif command == "move":
            scene.move(**kwargs)
        elif command == "rotate":
            scene.rotate(**kwargs)
        elif command == "attribute":
            renderer.set_attribute(**kwargs)
        elif command == "render":
            renderer.render(**kwargs)
            renderer.show_image()
        elif command == "show":
            renderer.show_image()
        elif command == "save":
            renderer.save_image(**kwargs)
        elif command == "help":
            help()
        else:
            print("Unknown command. Try 'help' for a list of commands.")

def parse_kwargs(args: List[str]):
    kwargs = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            kwargs[key] = float(value)  # Convert to float if you expect numerical values
    return kwargs


main()
