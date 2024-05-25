# Vsebuje Space razrede, ki enkapsulirajo logiko specifično za vsak space.

import typehints as th
import numpy as np
from typing import Tuple, List, Callable


from objects import _IntersectableObject, Sphere, Plane, _ObjectTypes

# ---------------------------- Stuff that makes it work ----------------------------

class _Space:
    def __init__(self) -> None:
        """ADD izpeljane formule funkcije ki direkt vrnejo parameter preseka v self.quick_intersect!!!"""
        self.quick_intersect = dict()
        self.type = _ObjectTypes.space
        self.name = "space"

    def __str__(self) -> str:
        return f"{self.type:<10} | {" ":<8} {" ":<8} {" ":<8} {" ":<8} {" ":<8}  "

    def set_attribute(self, attribute: str, value: float):
        """Set an attribute of the object."""
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            print(f"Attribute {attribute} does not exist.")
    # Če ta prostor rabi posebno funkcijo za presečišče uporabi:
    def intersects(self, position: np.ndarray = np.array([0, 0, 0]),
                   direction: np.ndarray = np.array([0, 0, 0]),
                   objects: List[_IntersectableObject] = list(),
                   max_distance: float = float("inf")) -> Tuple[_IntersectableObject, th.position]:
        """Če prostor ne rabi posebne funkcije za presečišče, ne implementiraj te funkcije!
        Poišče NAJBLIŽJE presečipče raya s sceno, vrne presekan objekt in točko preseka."""
        return -1

    # Če nima vsak objekt izpeljane formule uporabi:
    def get_xyz(self, position: np.ndarray, direction: np.ndarray, t: float) -> np.ndarray:
        """Če nimaš funkcije z izpeljano formulo za ta specifičn prostor, implementiraj to funkcijo.
        Returns a point (x, y, z) on the ray at the given parameter t."""
        raise NotImplementedError
    

class SpacesRegistry:
    spaces = dict()

    @classmethod
    def register(cls, name: str, space: _Space, help_msg: str):
        cls.spaces[name] = (space, help_msg)

    @classmethod
    def get(cls, name: str) -> _Space:
        return cls.spaces.get(name)
    
    @classmethod
    def get_all(cls) -> dict:
        return cls.spaces

# ---------------------------- SPACES ----------------------------
class Euclidean(_Space):
    def __init__(self) -> None:
        super().__init__()
        self.type = _ObjectTypes.space
        self.name = "euclidean"

    # Equation stuff
    def get_xyz(self, position: np.ndarray, direction: np.ndarray, t: float) -> np.ndarray:
        return position + direction * t
SpacesRegistry.register("Euclidean", Euclidean, 
                              "Euclidean space is a normal 3D space.\n" + 
                              "Usage: Euclidean")


class FlatTorus(_Space):
    def __init__(self, boundry_size: np.ndarray = np.array([10, 10, 10]),
                 repetitions: int = 10) -> None:
        super().__init__()
        self.boundry_size = boundry_size
        self.repetitions = repetitions
        self.type = _ObjectTypes.space
        self.name = "flattorus"

    def __str__(self) -> str:
        prev = super().__str__()
        return prev + f"boundry: {self.boundry_size} repetitions: {self.repetitions:<10} "

    # Seter geter

    @property
    def boundry_size(self) -> np.ndarray:
        return np.array([self.a, self.b, self.c])
    
    @boundry_size.setter
    def boundry_size(self, boundry_size: np.ndarray):
        self.a, self.b, self.c = boundry_size 

    # Equation stuff
    def get_xyz(self, position: np.ndarray, direction: np.ndarray, t: float) -> np.ndarray:
        x, y, z = position + direction * t
        x = x % self.a
        y = y % self.b
        z = z % self.c
        return np.array([x, y, z])
    
    def intersects(self, position: np.ndarray,
                   direction: np.ndarray,
                   objects: List[_IntersectableObject],
                   max_distance: float = float("inf")) -> Tuple[_IntersectableObject, th.position]:
        # Prep
        intersected_object = None
        closest_distance = float("inf")
        found_intersection = False
        max_t, max_t_direction = self._max_t(position, direction)

        for _ in range(int(self.repetitions)):
            for obj in objects:
                if hasattr(obj, "euclidean"): #If euclidean function is implemented
                    distance = obj.euclidean(position, direction)
                else:
                    # TODO Prepiš iz finc_intersection!!!
                    raise NotImplementedError
                
                if distance is not None and distance <= closest_distance and distance <= max_distance:
                    # Update the closest object, break
                    closest_distance = distance
                    intersected_object = obj
                    found_intersection = True
                
            # If we found an intersection, break
            if found_intersection:
                break
            else: 
                # Update the position, max_t for the next for iteration
                position = Euclidean.get_xyz(Euclidean(), position, direction, max_t)
                position[max_t_direction] = -position[max_t_direction] # Reflect
                max_t, max_t_direction = self._max_t(position, direction)

        if not intersected_object:
            return None, None
        
        # Calculate the intersection point
        intersection_point = Euclidean.get_xyz(Euclidean(), position, direction, closest_distance)
        return intersected_object, intersection_point
    
    def _max_t(self, position: np.ndarray, direction: np.ndarray) -> Tuple[float, int]:
        t = float("inf")
        min_t_in_direction = 0

        # Za x, y, z smer prever:
        for i in range(3):
            if direction[i] > 0:
                new_t = (self.boundry_size[i]/2 - position[i]) / direction[i]
                if new_t < t:
                    t = new_t
                    min_t_in_direction = i
            elif direction[i] < 0:
                new_t = (-self.boundry_size[i]/2 - position[i]) / direction[i] 
                if new_t < t:
                    t = new_t
                    min_t_in_direction = i

        # Če je je bil izven boundry
        if t < 0:
            raise ValueError("t < 0 -> ray is going away from the boundry. Is camera inside the boundry?")
        
        return (t, min_t_in_direction)
SpacesRegistry.register("FlatTorus", FlatTorus, 
                              "FlatTorus space is like a normal space in a cube with sides (a, b, c) (in order x, y, z), and when a ray reaches one side it teleports to the other side.\n" + 
                              "Usage: FlatTorus [boundry_size=(a, b, c)], [repetitions=10]")


class TwoSphere(_Space):
    def __init__(self, R: float = 10.0) -> None:
        super().__init__()
        self.R = R
        self.type = _ObjectTypes.space
        self.name = "twosphere" 
    
    def __str__(self) -> str:
        prev = super().__str__()
        return prev + f"R: {self.R:<10} "

    # Equation stuff
    def get_xyz(self, position: np.ndarray, direction: np.ndarray, t: float) -> np.ndarray:
        pass
SpacesRegistry.register("TwoSphere", TwoSphere, 
                              "TwoSphere space is a space where rays travel on the surface of a sphere with radius R.\n" + 
                              "Usage: TwoSphere [R=2]")










# Old code
    
    # # TODO: meki macroti / settingsi
    # radius = 2
    # center: th.position

    # def uvToVec(self, u: float, v:float) -> th.position:
    #     x = self.radius*math.cos(v)*math.sin(u)
    #     y = self.radius*math.sin(v)*math.sin(u)
    #     z = self.radius*math.cos(u)
    #     return (x, y, z)

    # def sphereCenter(self, position: th.position, direction: th.direction) -> th.position:
    #     radius = 2
    #     # cross product straight down x direction d(ray) -> circle plane normal n
    #     n=np.cross([0,0,-1], direction)
    #     # cross product direction x normal -> a vector in circle plane perpendicular to ray
    #     C=np.cross(direction, n)
    #     # normalize and extend to length R ... C = center of 2-sphere
    #     C=np.add(np.multiply(np.divide(C, np.linalg.norm(C)), self.radius), position)
    #     return C

    # def euler(self, y1: float, y2: float, y3: float, y4: float, h):
    #     y1n = y1 + h*y2
    #     y2n = y2 + h*math.cos(y1)*math.sin(y1)*(y4*y4)
    #     y3n = y3 + h*y4
    #     y4n = y4 + h*-2*(1/math.tan(y1))*y2*y4
    #     if(y1n == 0):
    #         h=h*2
    #         print("ha", h)
    #     return (y1n, y2n, y3n, y4n, h)

    # def initializeState(self, position: th.position, direction: th.direction, h) -> tuple[float, float, float, float]:
    #     self.center = self.sphereCenter(position, direction)
    #     # move to 0, 0, 0
    #     T = np.subtract(position, self.center)

    #     # Initial parameters
    #     # u
    #     y1 = math.acos(T[2]/self.radius)
    #     if(y1==0):
    #         y1=0.1;
    #     # v
    #     y3 = math.atan2(T[1], T[0])
    #     # du
    #     y2=1
    #     # dv
    #     y4=0

    #     # Calculate first point approximation
    #     y1n, y2n, y3n, y4n, h = self.euler(y1, y2, y3, y4, h)
    #     D = np.subtract(np.add(self.uvToVec(y1n, y3n), self.center), position)

    #     # Dot product of vector towards first point and expected direction should be positive,
    #     # otherwise change direction (intial parameters)
    #     if(np.dot(direction, D) < 0):
    #         y2 = -1

    #     return (y1, y2, y3, y4)


    # def move(self, state: tuple[float, float, float, float], h) -> tuple[tuple[float, float, float, float], int, th.position]:
    #     y1p = state[0]
    #     y2p = state[1]
    #     y3p = state[2]
    #     y4p = state[3]

    #     y1t, y2t, y3t, y4t, h = self.euler(y1p, y2p, y3p, y4p, h)
    #     x, y, z = np.add(self.uvToVec(y1t, y3t), self.center)

    #     return ((y1t, y2t, y3t, y4t), h, (x, y, z))