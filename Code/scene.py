# SCENE je entiteta, ki hrani objekte in jih dodaja, odstranjuje, premika..
from typing import List, Type, Dict
import curses
import time

import typehints as th
from spaces import _Space, Euclidean
from objects import _Scene_object



class Scene:
    space: Type[_Space]
    scene_contents: Dict[str, Type[_Scene_object]]
    signs: List[int]
    help_dict = {
        "add": "Usage: add <name> type=<object/light/camera> [position=(x, y, z)] [rotation=(u, v, w)] [visible=bool] \nFor spheare: [radious=float]",}

    def __init__(self, space: Type[_Space] = Euclidean(), 
                 scene_contents: Dict[str, Type[_Scene_object]] = None):
        self.space = space if space else Euclidean()
        self.scene_contents = scene_contents if scene_contents else dict()
        self.signs = list()

    # Get scene_contents by type
    @property
    def objects(self):
        return [obj for obj in self.scene_contents.valu() if th.ObjType.object in obj.type]

    @property
    def lights(self):
        return [obj for obj in self.scene_contents.values() if th.ObjType.light in obj.type]
    
    @property
    def cameras(self):
        return [obj for obj in self.scene_contents.values() if th.ObjType.camera in obj.type]
    
    # Controlling the scene
    def move(self, **kwargs):
        if ("name" not in kwargs) or (kwargs["name"] == "help"):
            help("move")
            return
        
        name = kwargs["name"]
        if name not in self.scene_contents.keys(): # Če ga ni nikjer
            print(f"{name} does not exist.")
            return

        obj = self.scene_contents.get(name)

        # INTERACTIVE MODE
        if len(kwargs) == 1:
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
                        obj.pos_x += 1
                    if key == ord('s'):
                        obj.pos_x -= 1
                    if key == ord('a'):
                        obj.pos_z += 1
                    if key == ord('d'):
                        obj.pos_z -= 1
                    if key == ord('r'):
                        obj.pos_y += 1
                    if key == ord('f'):
                        obj.pos_y -= 1

                    stdscr.addstr(1, 0, f"Position: {obj.pos_x}, {obj.pos_y}, {obj.pos_z}")
                    stdscr.clrtoeol()  # Clear to the end of the line
                    stdscr.refresh()
                    time.sleep(0.1)

            curses.wrapper(interactive_mode)
            return

        # PREASIGNED MODE
        obj: Type[_Scene_object] = self.scene_contents[name]
        if "dx" in kwargs:
            obj.pos_x += kwargs["dx"]
        if "dy" in kwargs:
            obj.pos_y += kwargs["dy"]
        if "dz" in kwargs:
            obj.pos_z += kwargs["dz"]
        if "x" in kwargs:
            obj.pos_x = kwargs["x"]
        if "y" in kwargs:
            obj.pos_y = kwargs["y"]
        if "z" in kwargs:
            obj.pos_z = kwargs["z"]
        else:
            print("No movement specified. Use move help")

    def rotate(self, **kwargs):
        if ("name" not in kwargs) or (kwargs["name"] == "help"):
            help("rotate")
            return
        
        name = kwargs["name"]
        if name not in self.scene_contents:
            print(f"{name} does not exist.")
            return

        obj = self.scene_contents.get(name)

        # INTERACTIVE MODE
        if len(kwargs) == 1:
            def interactive_mode(stdscr: curses.window):
                curses.curs_set(0)  # Hide cursor
                stdscr.nodelay(True)  # Non-blocking input
                stdscr.addstr(0, 0, "Interactive mode. Use 'u' 'j' for rot_u, 'i' 'k' for rot_v, 'o' 'l' for rot_w, 'q' to quit.")
                stdscr.refresh()
                
                while True:
                    key = stdscr.getch()
                    if key == ord('q'):
                        break
                    if key == ord('u'):
                        obj.rot_u += 1
                    if key == ord('j'):
                        obj.rot_u -= 1
                    if key == ord('i'):
                        obj.rot_v += 1
                    if key == ord('k'):
                        obj.rot_v -= 1
                    if key == ord('o'):
                        obj.rot_w += 1
                    if key == ord('l'):
                        obj.rot_w -= 1

                    stdscr.addstr(1, 0, f"Rotation: {obj.rot_u}, {obj.rot_v}, {obj.rot_w}")
                    stdscr.clrtoeol()  # Clear to the end of the line
                    stdscr.refresh()
                    time.sleep(0.1)

            curses.wrapper(interactive_mode)
            return

        # PRE-ASSIGNED MODE
        obj: Type[SceneObject] = self.scene_contents[name]
        if "du" in kwargs:
            obj.rot_u += kwargs["du"]
        if "dv" in kwargs:
            obj.rot_v += kwargs["dv"]
        if "dw" in kwargs:
            obj.rot_w += kwargs["dw"]
        if "u" in kwargs:
            obj.rot_u = kwargs["u"]
        if "v" in kwargs:
            obj.rot_v = kwargs["v"]
        if "w" in kwargs:
            obj.rot_w = kwargs["w"]
        else:
            print("No rotation specified. Use rotate help")

    def change_attribute(self, name: str, attribute: str, value):
        if name not in self.scene_contents:
            print(f"Object with name {name} does not exist.")
        else:
            obj = self.scene_contents[name]
            if hasattr(obj, attribute):
                setattr(obj, attribute, value)
                print(f"Changed {attribute} of {name} to {value}.")
            else:
                print(f"Object {name} has no attribute {attribute}.")

    def list(self):
            """Lists all the contents of the scene."""
            print("Scene contents:")
            header = f"{'Type':<10} | {'Name':<10} {'Pos_X':<8} {'Pos_Y':<8} {'Pos_Z':<8} {'Rot_U':<8} {'Rot_V':<8} {'Rot_W':<8}"
            print(header)
            print("-" * len(header))
            for obj in self.scene_contents.values():
                test = [1, 2, 3]
                print(f"{obj.type[0]:<10} | {obj.name:<10} {obj.pos_x:<8.2f} {obj.pos_y:<8.2f} {obj.pos_z:<8.2f} {obj.rot_u:<8.2f} {obj.rot_v:<8.2f} {obj.rot_w:<8.2f}")