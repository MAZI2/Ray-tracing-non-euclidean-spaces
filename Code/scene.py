# SCENE je entiteta, ki hrani objekte in jih dodaja, odstranjuje, premika..
from typing import List, Type, Dict
import curses
import time

import typehints as th
from spaces import _Space, Euclidean, SpacesRegistry
from objects import _SceneObject, _ObjectTypes, ObjectsRegistry


class Scene:
    
    def __init__(self, scene_contents: Dict[str, Type[_SceneObject]] = None):
        self.scene_contents = scene_contents if scene_contents else dict()
        self.signs = list()
        self.help_dict = {"move": "Move object. Usage: move <name> [dx=<dx>] [dy=<dy>] [dz=<dz>] [x=<x>] [y=<y>] [z=<z>]",
                          "rotate": "Rotate object. Usage: rotate <name> [du=<du>] [dv=<dv>] [dw=<dw>] [u=<u>] [v=<v>] [w=<w>]",
                          "list": "List all objects in the scene.",
                          "set_attribute": "Change attribute of the object. Usage: set_attribute <name> attribute=<attribute> value=<value>",
                          "add": "Add object to the scene. Usage: add <name> type=<type>\n" + "\n".join([f"    {key}: {help_string}" for key, (_, help_string) in ObjectsRegistry.get_all().items()]),
                          "remove": "Remove object from the scene. Usage: remove <name>",
                          "set_space": "Set the space of the scene. Usage: set_space <space>\n" + "\n".join([f"    {key}: {help_string}" for key, (_, help_string) in SpacesRegistry.get_all().items()]),
                          "help": "Get help for a command. Usage: help [<command>]"}

    # Get scene_contents by type
    @property
    def space(self):
        return [obj for obj in self.scene_contents.values() if _ObjectTypes.space == obj.type][0]
    
    @space.setter
    def space(self, space: Type[_Space]):
        # Check if there is already a space in the scene
        if _ObjectTypes.space in [obj.type for obj in self.scene_contents.values()]:
            for obj in self.scene_contents.values():
                if _ObjectTypes.space == obj.type:
                    del self.scene_contents[obj.name]
                    break
        self.scene_contents[space.name] = space
    
    @property
    def objects(self):
        return [obj for obj in self.scene_contents.values() if _ObjectTypes.object == obj.type]

    @property
    def lights(self):
        # For now all the objects just use the first light...
        return [obj for obj in self.scene_contents.values() if _ObjectTypes.light == obj.type]
    
    @property
    def cameras(self):
        # For now all the objects just use the first camera...
        return [obj for obj in self.scene_contents.values() if _ObjectTypes.camera == obj.type]
    
    # Controlling the scene
    def move(self, *args, **kwargs):
        obj = self._get_object("move", *args, **kwargs)
        if not obj:
            return

        # INTERACTIVE MODE
        if len(kwargs) == 0:
            def interactive_mode(stdscr: curses.window):
                curses.curs_set(0)  # Hide cursor
                stdscr.nodelay(True)  # Non-blocking input
                stdscr.addstr(0, 0, "Interactive mode. Use 'w' 'a' 's' 'd' for movement, 'r' / 'f' for up/down, 'q' to quit.")
                stdscr.refresh()
                
                while True:
                    key = stdscr.getch()
                    if key == ord('q'):
                        break
                    if key == ord('w'):
                        obj.move(dx=1)
                    if key == ord('s'):
                        obj.move(dx=-1)
                    if key == ord('a'):
                        obj.move(dz=1)
                    if key == ord('d'):
                        obj.move(dz=-1)
                    if key == ord('r'):
                        obj.move(dy=1)
                    if key == ord('f'):
                        obj.move(dy=-1)

                    stdscr.addstr(1, 0, f"Position: {obj.x}, {obj.y}, {obj.z}")
                    stdscr.clrtoeol()  # Clear to the end of the line
                    stdscr.refresh()
                    time.sleep(0.1)

            curses.wrapper(interactive_mode)
            return

        # Call the objects move
        obj.move(**kwargs)

    def rotate(self, *args,  **kwargs):
        obj = self._get_object("rotate", *args, **kwargs)
        if not obj:
            return

        # INTERACTIVE MODE
        if len(kwargs) == 0:
            def interactive_mode(stdscr: curses.window):
                curses.curs_set(0)  # Hide cursor
                stdscr.nodelay(True)  # Non-blocking input
                stdscr.addstr(0, 0, "Interactive mode. Use 'w' 'a' 's' 'd' for rotating aroung u and v, " + 
                              "'r' / 'f' for w (not supported yet), 'q' to quit.")
                stdscr.refresh()
                
                while True:
                    key = stdscr.getch()
                    if key == ord('q'):
                        break
                    if key == ord('w'):
                        obj.rotate(dv=1)
                    if key == ord('s'):
                        obj.rotate(dv=-1)
                    if key == ord('a'):
                        obj.rotate(du=1)
                    if key == ord('d'):
                        obj.rotate(du=-1)
                    if key == ord('r'):
                        obj.rotate(dw=1)
                    if key == ord('f'):
                        obj.rotate(dw=-1)

                    stdscr.addstr(1, 0, f"Rotation: {obj.u}, {obj.v}, {obj.w}")
                    stdscr.clrtoeol()  # Clear to the end of the line
                    stdscr.refresh()
                    time.sleep(0.1)

            curses.wrapper(interactive_mode)
            return

        # Call the objects rotate
        obj.rotate(**kwargs)

    def set_attribute(self, *args, **kwargs):
        obj = self._get_object("set_attribute", *args, **kwargs)
        if not obj:
            return

        if len(kwargs) < 1:
            print("Attribute and provided.")
            help("set_attribute")
            return
        
        for key in kwargs.keys():
            obj.set_attribute(key, kwargs[key])

    def add(self, *args, **kwargs):
        if len(args) < 1:
            print("Name or type not provided.")
            help("add")
            return
        
        name = args[0]
        if "type" in kwargs:
            type = kwargs["type"]
        else:
            type = args[0]

        if type not in ObjectsRegistry.get_all().keys():
            print(f"Type {type} does not exist.")
            return
        
        if name in self.scene_contents.keys():
            print(f"{name} already exists.")
            return
        
        obj = ObjectsRegistry.get(type)(**kwargs)
        self.scene_contents[name] = obj

    def remove(self, *args, **kwargs):
        obj = self._get_object("remove", *args, **kwargs)
        if not obj:
            return
        
        name = args[0]
        
        del self.scene_contents[name]

    def set_space(self, *args, **kwargs):
        if len(args) < 1:
            print("Space not provided.")
            help("set_space")
            return
        
        space = args[0]
        if space not in ObjectsRegistry.get_all().keys():
            print(f"Space {space} does not exist.")
            return
        
        self.space = ObjectsRegistry.get(space)(**kwargs)

    def list(self):
            """Lists all the contents of the scene."""
            header = f"{'Name':<10} {'Type':<10} | {'x':<8} {'y':<8} {'z':<8} {'u':<8} {'v':<8}"
            print(header)
            print("-" * len(header))
            for name, obj in self.scene_contents.items():
                print(f"{name:<10} {obj}")

    def help(self, *args, **kwargs):
        if len(args) > 0:
            command = args[0]

            if command in self.help_dict:
                print(self.help_dict.get(command))
                return
            
        # Pač ni najdu nekak
        print("Available commands:")
        for key, value in self.help_dict.items():
            print(f"  {key}: {value}")
    
    def render_check(self, *args, **kwargs):
        if _ObjectTypes.camera not in [obj.type for obj in self.scene_contents.values()]:
            print("No camera in the scene.")
            return False
        if _ObjectTypes.light not in [obj.type for obj in self.scene_contents.values()]:
            print("No light in the scene.")
            return False
        if _ObjectTypes.space not in [obj.type for obj in self.scene_contents.values()]:
            print("No space in the scene.")
            return False
        return True
    
    # Helper functions
    def _get_object(self, help_for: str, *args, **kwargs) -> _SceneObject:
        if len(args) < 1 or args[0] == "help":
            self.help(help_for)
            return None
        
        name = args[0]

        if name not in self.scene_contents.keys(): # Če ga ni nikjer
            print(f"{name} does not exist.")
            return None

        obj = self.scene_contents.get(name)
        return obj
