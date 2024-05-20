# Razredi za vsak objekt ki je lahko v sceni. 

import typehints as th
import numpy as np


# -------------------- Objekti v sceni --------------------
# Vsi objekti v sceni morjo bit otrok _Object objekta.

class _Object:
    """Objekt v sceni, k bo vidn rayem"""
    position: th.position
    rotation: th.rotation
    color: th.color
    visible: bool

    def __init__(self, position: th.position, rotation: th.rotation, color: th.color, visible: bool):
        self.position = position
        self.rotation = rotation
        self.color = color
        self.visible = visible

    def sign(self, position: th.position) -> int:
        pass

    def dist(self, position: th.position) -> float:
        pass


class Sphere(_Object):
    radius: float

    def __init__(self, position: th.position, rotation: th.rotation, color: th.color, visible: bool, radius: float):
        super().__init__(position, rotation, color, visible) # Rotation sm dodal da so vsi scene objects enotni.
        self.radius = radius

    def sign(self, position: th.position) -> int:
        return np.sign(self.dist(position))

    def dist(self, position: th.position) -> float:
        return np.linalg.norm(np.subtract(position, self.position)) - self.radius * self.radius


class Plane(_Object):

    def __init__(self, position: th.position, rotation: th.rotation, color: th.color, visible: bool):
        super().__init__(position, rotation, color, visible) # Rotation je smer normale na ravnino.

    def sign(self, position: th.position) -> int:
        pass

    def dist(self, position: th.position) -> float:
        pass



# -------------------- Lights --------------------

class Light:
    posiition: th.position
    color: th.color
    visible: bool

    def __init__(self, position: th.position, color: th.color, visible: bool):
        self.position = position
        self.color = color
        self.visible = visible

# -------------------- Cameras --------------------

class Camera:
    posiition: th.position
    rotation: th.rotation
    fov: float
    resolution: th.resolution

    def __init__(self, position: th.position, rotation: th.rotation, fov: float, resolution: th.resolution):
        self.position = position
        self.rotation = rotation
        self.fov = fov # Diagonaln Field of view (v stopinjah)
        self.resolution = resolution # (width, height) 0-inf

