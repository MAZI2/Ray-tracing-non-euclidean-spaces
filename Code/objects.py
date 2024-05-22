# Razredi za vsak objekt ki je lahko v sceni. 

import typehints as th
import numpy as np

class _Scene_object:
    """Katerakol stvar, ki jo lahko damo v sceno."""
    
    def __init__(self, name: str, type: list[str], position: th.position, rotation: th.rotation, visible: bool):
        self.name = name
        self.type = type
        self.visible = visible
        # Position
        self.pos_x, self.pos_y, self.pos_z = position
        # Rotation
        self.rot_u, self.rot_v, self.rot_w = rotation

    def sign(self, position: th.position) -> int:
        raise NotImplementedError

    def dist(self, position: th.position) -> float:
        raise NotImplementedError
    
    # Getters, setters for position and rotation easyer use.
    @property
    def position(self) -> th.position:
        return (self.pos_x, self.pos_y, self.pos_z)
    
    @position.setter
    def position(self, position: th.position):
        self.pos_x, self.pos_y, self.pos_z = position

    @property
    def rotation(self) -> th.rotation:
        return (self.rot_u, self.rot_v, self.rot_w)
    
    @rotation.setter
    def rotation(self, rotation: th.rotation):
        self.rot_u, self.rot_v, self.rot_w = rotation

# -------------------- Objekti v sceni --------------------

class Sphere(_Scene_object):
    radius: float

    color: th.color

    def __init__(self, name: str, position: th.position, rotation: th.rotation, radius: float, color: th.color = (255, 255, 255), visible: bool = True):
        super().__init__(name, [th.ObjType.object, th.ObjType.sphere], position, rotation, visible) # Rotation sm dodal da so vsi scene objects enotni.
        self.radius = radius
        self.color = color

    def sign(self, position: th.position) -> int:
        return np.sign(self.dist(position))

    def dist(self, position: th.position) -> float:
        return np.linalg.norm(np.subtract(position, self.position)) - self.radius * self.radius


class Plane(_Scene_object):
    color: th.color

    def __init__(self, name: str, position: th.position, color: th.color = (255, 255, 255)):
        super().__init__(name, [th.ObjType.object, th.ObjType.plane], position, (0, 0, 0), True) # Rotation je smer normale na ravnino.
        self.color = color

    def sign(self, position: th.position) -> int:
        pass

    def dist(self, position: th.position) -> float:
        pass



# -------------------- Lights --------------------

class Light(_Scene_object):
    color: th.color

    def __init__(self, name: str, position: th.position, color: th.color = (255, 255, 255)):
        super().__init__(name, [th.ObjType.light], position, (0, 0, 0), True)
        self.color = color


# -------------------- Cameras --------------------

class Camera(_Scene_object):
    fov: float

    def __init__(self, name: str, position: th.position, rotation: th.rotation, fov: float = 70):
        super().__init__(name, [th.ObjType.camera], position, rotation, True)
        self.fov = fov # Diagonaln Field of view (v stopinjah)
