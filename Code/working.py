import threading
import queue
import re
from typing import List, Tuple

import typehints as th
from ui import UI
from scene import Scene
from render import Renderer
from spaces import Euclidean, FlatTorus, TwoSphere
from objects import Plane, Light, Camera, Sphere

import logging
logger = logging.getLogger(__name__)

class _WorkingEvents:
    quit = "quit"

_working_queue = queue.Queue()

class Working:
    def __init__(self):
        pass

    def __del__(self):
        self.stop_thread()
    
    def stop_thread(self):
        _working_queue.put(_WorkingEvents.quit)
        # self.thread.join() Doesnt need to be joined, because it is a daemon thread

    def start_thread(self):
        self.thread = _WorkingThread()
        self.thread.start()
    

class _WorkingThread(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.daemon = True # Kill thread when main thread dies
        self.scene = Scene({"sphere1": Sphere((3, 0, 0), 1, (255, 0, 255)), 
                            "sphere2": Sphere((1.8, 0.8, 1), 0.2, (0, 255, 255)), 
                            # "plane": Plane((0, -2, 0), (0, 1, 0), (255, 100, 0)),
                            "light": Light((0, 3, 3), ), 
                            "camera": Camera((0, 0, 0), (0, 0, 0), 127),
                            "flattorus": FlatTorus((10, 10, 10), 5)})
        self.renderer = Renderer(self.scene)

    def run(self):
        while True:
            print()
            line = input("Raytracer>  ")
            if not line:
                if self.check_queue():
                    return
                continue

            tokens = self._split_line(line)
            command = tokens[0]
            if len(tokens) > 1:
                args, kwargs = self._parse_kwargs(tokens[1:])
            else:
                args = []
                kwargs = {}

            if command == "quit":
                break
            elif command == "list":
                self.scene.list()
            elif command == "move":
                self.scene.move(*args, **kwargs)
            elif command == "rotate":
                self.scene.rotate(*args, **kwargs)
            elif command == "set_attribute":
                self.scene.set_attribute(*args, **kwargs)
            elif command == "add":
                self.scene.add(*args, **kwargs)
            elif command == "remove":
                self.scene.remove(*args)
            elif command == "render":
                if self.scene.render_check():
                    image = self.renderer.render(**kwargs)
                    UI.set_image(image)
            elif command == "help":
                self.scene.help(*args)
            else:
                print("Unknown command. Try 'help' for a list of commands.")

        if self.check_queue():
            return

    
    def check_queue(self):
        if not _working_queue.empty():
            task = _working_queue.get()
            if task == _WorkingEvents.quit:
                return True
        return False

    # Helper methods

    @staticmethod
    def _split_line(line: str) -> List[str]:
        tokens = re.findall(r'[^\s=]+=[^\s]*\(.*?\)|[^\s()]+', line)
        return tokens

    @staticmethod
    def _parse_kwargs(args: List[str]) -> Tuple[tuple, dict]:
        return_args = list()
        kwargs = dict()
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                # Value is eather a float or a string or a tuple
                try:
                    value = float(value)
                except ValueError:
                    if value[0] == "(" and value[-1] == ")":
                        value = tuple(map(float, value[1:-1].split(", ")))
                    else:
                        pass
                kwargs[key] = value
            else:
                return_args.append(arg)
        return_args = tuple(return_args)
        return (return_args, kwargs)
