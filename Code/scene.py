# SCENE je entiteta, ki hrani objekte in jih dodaja, odstranjuje, premika..
from typing import List, Type, Dict

import typehints as th
from spaces import _Space, Euclidean
from objects import _Scene_object, Light, Camera



class Scene:
    space: Type[_Space]
    objects: Dict[str, Type[_Scene_object]]
    light: Light
    camera: Camera
    signs: List[int]

    def __init__(self, space: Type[_Space] = Euclidean(), 
                 objects: Type[_Scene_object] = None, 
                 lights: Type[Light] = None, 
                 camera: Type[Camera] = None):
        
        self.space = space
        self.objects = objects
        self.light = lights
        self.camera = camera
        self.signs = list()

    def add(self, obj: Type[_Scene_object]):
        if isinstance(obj, Light): # Doda na pravo mesto
            self._light = obj
        elif isinstance(obj, Camera):
            self._camera = obj
        else:
            self._objects[obj.name] = obj

    def remove(self, name: str):
        if name not in self.objects and name != self.light.name and name != self.camera.name: # Če ga ni nikjer
            print(f"{name} does not exist.")
        else:
            if name == self.light.name:
                self._light = None
            elif name == self.camera.name:
                self._camera = None
            else:
                self.objects.pop(name)

    def move(self, name: str, dx = 0, dy = 0, dz = 0, x = None, y = None, z = None):
        if name not in self.objects and name != self.light.name and name != self.camera.name:
            print(f"{name} does not exist.")
        else:
            obj: Type[_Scene_object] = self.objects[name]
            pos = obj.position # Trenutna pozicija (x, y, z)
            obj.position = ((x if x else pos[0]) + dx, # Če x ni None, uporabi x, sicer uporabi pos[0]
                             (y if y else pos[1]) + dy, 
                             (z if z else pos[2]) + dz)

    def change_attribute(self, name: str, attribute: str, value):
        if name not in self.objects:
            print(f"Object with name {name} does not exist.")
        else:
            obj = self.objects[name]
            if hasattr(obj, attribute):
                setattr(obj, attribute, value)
                print(f"Changed {attribute} of {name} to {value}.")
            else:
                print(f"Object {name} has no attribute {attribute}.")

