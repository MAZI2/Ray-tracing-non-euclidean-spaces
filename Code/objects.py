# Razredi za vsak objekt ki je lahko v sceni. 

import typehints as th

class _Scene_object:
    """Katerakol stvar, ki jo lahko damo v sceno."""
    name: str
    position: th.position
    rotation: th.rotation
    visible: bool

    def __init__(self, name: str, position: th.position, rotation: th.rotation, visible: bool):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.visible = visible

    # Getters & Setters


# -------------------- Objekti v sceni --------------------

class Sphere(_Scene_object):
    radius: float

    color: th.color

    def __init__(self, name: str, position: th.position, rotation: th.rotation, color: th.color, visible: bool, radius: float):
        super().__init__(name, position, rotation, visible) # Rotation sm dodal da so vsi scene objects enotni.
        self.radius = radius
        self.color = color

    def sign(self, position: th.position) -> int:
        pass


class Plane(_Scene_object):
    color: th.color

    def __init__(self, name: str, position: th.position, color: th.color = (255, 255, 255)):
        super().__init__(name, position, (0, 0, 0), True) # Rotation je smer normale na ravnino.
        self.color = color

    def sign(self, position: th.position) -> int:
        pass


# -------------------- Lights --------------------

class Light(_Scene_object):
    color: th.color

    def __init__(self, name: str, position: th.position, color: th.color = (255, 255, 255)):
        super().__init__(name, position, (0, 0, 0), True)
        self.color = color


# -------------------- Cameras --------------------

class Camera(_Scene_object):
    fov: float
    resolution: th.resolution

    def __init__(self, name: str, position: th.position, rotation: th.rotation, fov: float = 70, resolution: th.resolution = (960, 540)):
        super().__init__(name, position, rotation, True)
        self.fov = fov # Diagonaln Field of view (v stopinjah)
        self.resolution = resolution # (width, height) 0-inf

