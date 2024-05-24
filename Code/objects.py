# Razredi za vsak objekt ki je lahko v sceni. 

import typehints as th
import numpy as np

class _ObjectTypes:
    intersectable_object = "intersectable_object"
    sphere = "sphere"
    plane = "plane"
    light = "light"
    camera = "camera"


class _SceneObject:
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

class _IntersectableObject(_SceneObject):
    def __init__(self, name: str, subtype: str, position: th.position, rotation: th.rotation, color: th.color, visible: bool):
        super().__init__(name, [_ObjectTypes.intersectable_object, subtype], position, rotation, visible)
        self.color_r, self.color_g, self.color_b = color

    def sign(self, position: th.position) -> int:
        raise NotImplementedError

    def dist(self, position: th.position) -> float:
        raise NotImplementedError
    
    # Getters, setters for position and rotation easyer use.
    @property
    def color(self) -> th.color:
        return (self.color_r, self.color_g, self.color_b)
    
    @color.setter
    def color(self, color: th.color):
        self.color_r, self.color_g, self.color_b = color

class Sphere(_IntersectableObject):
    radius: float

    def __init__(self, name: str, position: th.position, radius: float, color: th.color = (255, 255, 255), visible: bool = True):
        super().__init__(name, _ObjectTypes.sphere, position, (0, 0, 0), color, visible)
        self.radius = radius

    def sign(self, position: th.position) -> int:
        return np.sign(self.dist(position))

    def dist(self, position: th.position) -> float:
        return np.linalg.norm(np.subtract(position, self.position)) - self.radius * self.radius


class Plane(_IntersectableObject):

    def __init__(self, name: str, position: th.position, normal: th.rotation, color: th.color = (255, 255, 255), visible: bool = True):
        super().__init__(name, _ObjectTypes.plane, position, normal, color, visible)


    def sign(self, position: th.position) -> int:
        pass

    def dist(self, position: th.position) -> float:
        pass



# -------------------- Lights --------------------

class Light(_SceneObject):
    color: th.color

    def __init__(self, name: str, position: th.position, color: th.color = (255, 255, 255)):
        super().__init__(name, [_ObjectTypes.light], position, (0, 0, 0), True)
        self.color = color


# -------------------- Cameras --------------------

class Camera(_SceneObject):
    fov: float

    def __init__(self, name: str, position: th.position, rotation: th.rotation, fov: float = 90):
        super().__init__(name, [_ObjectTypes.camera], position, rotation, True)
        self.fov = fov # Diagonaln Field of view (v stopinjah)
