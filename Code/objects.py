# Razredi za vsak objekt ki je lahko v sceni. 

import typehints as th
import numpy as np

from utilities import vector_uvw

# -------------------- Stuff that makes it work --------------------

class _SceneObject:
    """Katerakol stvar, ki jo lahko damo v sceno."""
    def __init__(self,
                 position: np.ndarray, 
                 orientation: np.ndarray, 
                 visible: bool):
        self.type = "implement me u bastard!"
        self.visible = visible
        # Position
        self.x, self.y, self.z = position
        # orientation
        self.u, self.v, self.w = orientation
        # Name
        self.name = "sceneobject"
    
    def move(self, x: float = 0, y: float = 0, z: float = 0, 
             dx: float = 0, dy: float = 0, dz: float = 0):
        self.x = x if not dx else self.x + dx # Tko sm napisu da da dx prednost če se zatipkaš
        self.y = y if not dy else self.y + dy
        self.z = z if not dz else self.z + dz
    
    def rotate(self, u: float = 0, v: float = 0, w: float = 0, 
               du: float = 0, dv: float = 0, dw: float = 0):
        self.u = u if not du else self.u + du
        self.v = v if not dv else self.v + dv
        self.w = w if not dw else self.w + dw #Is not used yet
    
    def set_attribute(self, attribute: str, value: float):
        """Set an attribute of the object."""
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            print(f"Attribute {attribute} does not exist.")
    
    def __str__(self) -> str:
        return f"{self.type:<10} | {self.x:<8.2f} {self.y:<8.2f} {self.z:<8.2f} {self.u:<8.2f} {self.v:<8.2f} "

    # Getters, setters for position and orientation easyer use.
    @property
    def position(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])
    
    @position.setter
    def position(self, position: np.ndarray):
        self.x, self.y, self.z = position

    @property
    def orientation(self) -> np.ndarray:
        return np.array([self.u, self.v, self.w])
    
    @orientation.setter
    def orientation(self, orientation: np.ndarray):
        self.u, self.v, self.w = orientation

class _ObjectTypes:
    """Types of objects that can be in the scene."""
    object = "object"
    light = "light"
    camera = "camera"
    space = "space"


class ObjectsRegistry:
    """Register for all objects that exist"""
    _objects = dict()

    @classmethod
    def register(cls, name: str, object: _SceneObject, help_msg: str):
        cls._objects[name] = (object, help_msg)

    @classmethod
    def get(cls, name: str) -> _SceneObject:
        return cls._objects.get(name)[0]
    
    @classmethod
    def get_all(cls) -> dict:
        return cls._objects


# -------------------- Objekti v sceni --------------------

class _IntersectableObject(_SceneObject):
    def __init__(self, position: np.ndarray, 
                 orientation: np.ndarray,  
                 rgb: th.rgb,
                 visible: bool):
        super().__init__(position, orientation, visible)
        self.type = _ObjectTypes.object
        self.rgb = rgb
        self.name = "object"


    # Getters, setters for position and orientation easyer use.
    @property
    def rgb(self) -> np.ndarray: # int8!
        return np.array([self._rgb_r, self._rgb_g, self._rgb_b], dtype=np.uint8)
    
    @rgb.setter
    def rgb(self, rgb: th.rgb):
        self._rgb_r, self._rgb_g, self._rgb_b = rgb

    # Če objekt nima specific izpeljave za vse prostore more implementirat:
    def equation(self, point: np.ndarray) -> float:
        """Vsak objekt ki nima specific izpeljave za vsak prostor naj implementira to funkcijo.
        Vrne vrednost neke enačbe, ki je = 0 samo če je točka na objektu. Za sphere npr ||point - center|| - radius"""
        raise NotImplementedError

    # Space specific izpeljave: Ime funkcije more bit isti imenu prostora
    def euclidean(self, position: np.ndarray, direction: np.ndarray) -> float:
        """Specifično izpeljane formule morjo met ime funkcije enako imenu prostora.
        Specifično izpeljana funkcija ki vrne parametr t kjer se ray seka za evklidski prostor."""
        raise NotImplementedError

class Sphere(_IntersectableObject):
    def __init__(self, position: np.ndarray = np.array([10, 0, 0]),
                 radius: float = 1, 
                 rgb: np.ndarray = np.array([255, 255, 255]),
                 visible: bool = True):
        super().__init__(position, (0, 0, 0), rgb, visible)
        self.radius = radius
        self.type = _ObjectTypes.object
        self.name = "sphere"

    # For scene:
    def rotate(self, u: float = 0, v: float = 0, w: float = 0, du: float = 0, dv: float = 0, dw: float = 0):
        print("Spheres are round u know...")
        pass # Spheres don't rotate
    
    def __str__(self) -> str:
        return f"{super().__str__()} rgb: {self.rgb} R: {self.radius:<8.2f} "
    
    # For tangent method:
    def equation(self, point: np.ndarray) -> float:
        squared_distance = np.sum((point - self.position)**2) # kvadrat dolžine vektorja
        squared_radius = self.radius**2
        return squared_distance - squared_radius
    
    # For spaces:
    def euclidean(self, position: np.ndarray, direction: float) -> float:
        cur_position = position + direction * 0.001 # Move the position a bit forward ker mam nek weird bug
        L = np.subtract(cur_position, self.position) # Točka premice - središče krogle

        # a, b, c iz enačbe za ničle kvadratne funkcije:
        a = np.dot(direction, direction)
        b = 2 * np.dot(L, direction)
        c = np.dot(L, L) - self.radius**2

        # Diskriminanta:
        D_cube = b**2 - 4 * a * c
        if D_cube < 0:
            return None
        D = np.sqrt(D_cube)

        # Rešitvi:
        t1 = (-b + D) / (2 * a)
        t2 = (-b - D) / (2 * a)

        # Vrne najbližjo rešitev ki je v smeri direction (in presećišče obvi)
        if t1 < 0 and t2 < 0:
            return None
        if t1 < 0:
            return t2
        if t2 < 0:
            return t1
        return t1 if t1 < t2 else t2
ObjectsRegistry.register("sphere", Sphere, 
                                "Use: type=sphere position=<(x, y, z)> radius=<radius> [rgb=(r, g, b)] [visible=<True/False>]")

class Plane(_IntersectableObject):
    def __init__(self, position: np.ndarray = np.array([0, 0, 0]),
                 normal: np.ndarray = np.array([0, 1, 0]),
                 rgb: np.ndarray = np.array([255, 255, 255]),
                 visible: bool = True):
        super().__init__(position, (0, 0, 0), rgb, visible)
        self.normal = normal

        self.d = np.dot(self.normal, self.position)

        self.type = _ObjectTypes.object
        self.name = "plane"

    # Getters, setters for normal
    @property
    def normal(self) -> np.ndarray:
        return np.array([self.a, self.b, self.c])
    
    @normal.setter
    def normal(self, normal: np.ndarray):
        self.a, self.b, self.c = normal
        self.u, self.v, self.w = vector_uvw.vector_to_degrees(normal)

    @property
    def orientation(self) -> np.ndarray:
        return np.array([self.u, self.v, self.w])
    
    @orientation.setter
    def orientation(self, orientation: np.ndarray):
        self.normal = vector_uvw.degrees_to_vector(orientation) # Normal setter sets uvw
        self.d = np.dot(self.normal, self.position)
    
    # Scene called functions
    def move(self, x: float = 0, y: float = 0, z: float = 0, dx: float = 0, dy: float = 0, dz: float = 0):
        super().move(x, y, z, dx, dy, dz)
        self.d = np.dot(self.normal, self.position)
    
    def rotate(self, u: float = 0, v: float = 0, w: float = 0, du: float = 0, dv: float = 0, dw: float = 0):
        super().rotate(u, v, w, du, dv, dw)
        self.normal = vector_uvw.degrees_to_vector((self.u, self.v, self.w))
        self.d = np.dot(self.normal, self.position)

    def __str__(self) -> str:
        return f"{super().__str__()} rgb: {self.rgb} N: {self.normal}"

    # For tangent method:
    def equation(self, point: np.ndarray) -> float:
        return np.dot(self.normal, point) - self.d
    
    # For spaces:
    def euclidean(self, position: np.ndarray, direction: float) -> float:
        cur_position = position + direction * 0.001 # Move the position a bit forward ker mam nek weird bug

        stevec = np.dot(self.normal, np.subtract(self.position, cur_position))
        imenovalec = np.dot(self.normal, direction)

        # Če je imenovalec 0, pol vzporedno z ravnino
        if np.isclose(imenovalec, 0):
            return None
        
        t = stevec / imenovalec

        # Če mn kt 0 je za kamero
        if t < 0:
            return None
        
        return t
ObjectsRegistry.register("plane", Plane, 
                                "Use: type=plane position=<(x, y, z)> normal=<(u, v, 0)> [rgb=(r, g, b)] [visible=<True/False>]")


# -------------------- Lights --------------------

class Light(_SceneObject):
    def __init__(self, position: np.ndarray, 
                 rgb: np.ndarray = np.array([255, 255, 255])):
        super().__init__(position, (0, 0, 0), True)
        self.rgb = rgb

        self.type = _ObjectTypes.light
        self.name = "light"
    
    def __str__(self) -> str:
        return f"{super().__str__()} rgb: {self.rgb}"
ObjectsRegistry.register("light", Light, 
                                "Use: type=light position=<(x, y, z)> [rgb=(r, g, b)]")


# -------------------- Cameras --------------------

class Camera(_SceneObject):
    def __init__(self, position: np.ndarray, 
                 orientation: np.ndarray, 
                 fov: float = 127):
        super().__init__(position, orientation, True)
        self.fov = fov # Diagonaln Field of view (v stopinjah)

        self.type = _ObjectTypes.camera
        self.name = "camera"
    
    def __str__(self) -> str:
        return f"{super().__str__()} fov: {self.fov}"
ObjectsRegistry.register("camera", Camera, 
                                "Use: type=camera position=<(x, y, z)> orientation=<(u, v, w)> [fov=<fov>]")
