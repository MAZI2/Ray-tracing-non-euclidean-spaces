import threading
import queue
from typing import List

import typehints as th
from ui import UI
from scene import Scene
from render import Renderer
from spaces import Euclidean
from objects import Plane, Light, Camera

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
        self.scene = Scene(Euclidean(), {"plane": Plane("plane", (10, 0, 0)), "light": Light("light", (10, 10, 0), ), "camera": Camera("camera", (0, 0, 0), (0, 0, 0))})
        self.renderer = Renderer(self.scene, (800, 600))

    def run(self):
        while True:
            print()
            line = input("Raytracer>  ")
            if not line:
                if self.check_queue():
                    return
                continue

            tokens = line.split(" ")
            command = tokens[0]
            if len(tokens) > 1:
                kwargs = self._parse_kwargs(tokens[1:])
                kwargs["name"] = tokens[1]
            else:
                kwargs = {}

            if command == "quit":
                break
            elif command == "list":
                self.scene.list()
            elif command == "move":
                self.scene.move(**kwargs)
            elif command == "rotate":
                self.scene.rotate(**kwargs)
            elif command == "render":
                image = self.renderer.render(**kwargs)
                UI.set_image(image)
            elif command == "help":
                help()
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
    def _parse_kwargs(args: List[str]):
        kwargs = {}
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                kwargs[key] = float(value)  # Convert to float if you expect numerical values
        return kwargs
