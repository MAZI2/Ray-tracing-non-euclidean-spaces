import threading
import queue
import re
from typing import List, Tuple
import difflib

import typehints as th
from ui import UI
from scene import Scene
from render import Renderer
from utilities import Logger

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
        self.name = "WorkingThread" # Name the thread

        self.scene = Scene()
        self.renderer = Renderer()

        self.running = True

        self.logger = Logger.setup_logger("WorkingThread")
        self.logger.info("Working thread started.")

    def run(self):
        commands = {
            "quit": self.quit,
            "list": self.scene.list,
            "move": self.scene.move,
            "rotate": self.scene.rotate,
            "set_attribute": self.scene.set_attribute,
            "add": self.scene.add,
            "remove": self.scene.remove,
            "render": self.render,
            "render_sync": self.render_sync,
            "set_space": self.scene.set_space,
            "help": self.scene.help,
            "plot": self.plot,
            "set_scale": UI.set_scale,
            "set_resolution": self.scene.set_resolution,
        }

        while self.running:
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
                self.logger.debug(f"Command: {command}, args: {args}, kwargs: {kwargs}")
            else:
                args = []
                kwargs = {}

            if command in commands:
                try:
                    commands[command](*args, **kwargs)
                except TypeError as e:
                    print(f"Error: {e}")
                    print(f"Usage for '{command}': {commands[command].__doc__}")
                    self.logger.error(f"Error: {e}")
            else:
                # Provide suggestions for close matches
                suggestions = difflib.get_close_matches(command, commands.keys())
                if suggestions:
                    print(f"Unknown command '{command}'. Did you mean: {', '.join(suggestions)}?")
                else:
                    print(f"Unknown command '{command}'. Try 'help' for a list of commands.")


            if self.check_queue():
                self.logger.info("Quitting thread.")
                return

    
    def check_queue(self):
        if not _working_queue.empty():
            task = _working_queue.get()
            if task == _WorkingEvents.quit:
                return True
        return False

    # Commands with methods
    def quit(self):
        UI.stop_thread()
        self.running = False
    
    def render(self, *args, **kwargs):
        if self.scene.render_check():
            kwargs["scene"] = self.scene
            self.renderer.render(**kwargs)

    def render_sync(self, *args, **kwargs):
        if self.scene.render_check():
            kwargs["scene"] = self.scene
            self.renderer.render_sync(**kwargs)

    def plot(self, *args, **kwargs):
        if self.scene.render_check():
            kwargs["scene"] = self.scene
            if kwargs.get("name") is None and args:
                kwargs["name"] = args[0]
            else:
                print("No name provided.")
                return
            self.renderer.plot(**kwargs)
        
    
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
                    if len(value) > 2 and value[0] == "(" and value[-1] == ")":
                        value = tuple(map(float, value[1:-1].split(", ")))
                    else:
                        pass
                kwargs[key] = value
            else:
                return_args.append(arg)
        return_args = tuple(return_args)
        return (return_args, kwargs)
