# Vsebuje Space razrede, ki enkapsulirajo logiko specifično za vsak space.

import typehints as th
import numpy as np
from typing import Tuple, List, Callable

from objects import _IntersectableObject, Sphere, Plane, Light
from utilities import Ray, Logger, vector_uvw
from typehints import _ObjectTypes
from methods import broyden, adaptive_step_broyden, adaptive_step


# ---------------------------- Stuff that makes it work ----------------------------

class _Space:
    def __init__(self) -> None:
        """ADD izpeljane formule funkcije ki direkt vrnejo parameter preseka v self.quick_intersect!!!"""
        super().__init__()
        self.quick_intersect = dict() 
        self.type = _ObjectTypes.space
        self.name = "space"

        self.logger = Logger.setup_logger("Space")

    def __str__(self) -> str:
        return f"{self.type:<10} | {" ":<8} {" ":<8} {" ":<8} {" ":<8} {" ":<8}  "

    def set_attribute(self, attribute: str, value: float):
        """Set an attribute of the object."""
        if hasattr(self, attribute):
            setattr(self, attribute, value)
        else:
            print(f"Attribute {attribute} does not exist.")
    
        # Če nima vsak objekt izpeljane formule uporabi:
    
    # Vsak prostor implementira:
    def xyz_equation(self, ray: Ray, t: float) -> np.ndarray:
        """Equation that gets a parameter t and returns a point on the ray
        Every space must implement"""
        raise NotImplementedError
    
    # Prostor naj implementira eno od:
    def get_intersections(self, ray: Ray = Ray(np.array([0, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 0])),
                   objects: List[_IntersectableObject] = list(),
                   max_distance: float = float("inf")) -> Tuple[_IntersectableObject, th.position]:
        """Vrne (Objekt, točka) kjer se žark seka z nekim objektom v sceni.
        Implementiraj to al pa get_intesection."""
        return -1

    def get_intersection(self, ray: Ray, object: _IntersectableObject) -> float:
        """Vrne parameter t (ki ga ustavš v xyz_equation) točke sekanja žarka in objekta.
        Implementiraj to al pa get_intersections."""
        return adaptive_step(ray, object, self)

class SpacesRegistry: # TODO Vsak objekt svoj __doc__ in ne kle notr
    spaces = dict()

    @classmethod
    def register(cls, name: str, space: _Space, help_msg: str):
        cls.spaces[name] = (space, help_msg)

    @classmethod
    def get(cls, name: str) -> _Space:
        return cls.spaces.get(name)[0]
    
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
    def xyz_equation(self, ray: Ray, t: float) -> np.ndarray:
        return ray.origin + ray.direction * t
SpacesRegistry.register("euclidean", Euclidean, 
                              "Euclidean space is a normal 3D space.\n" + 
                              "      Usage: Euclidean")


class FlatTorus(_Space):
    def __init__(self, repetitions: int = 30,
                 boundry_size: np.ndarray = np.array([20, 20, 20])) -> None:
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
    def xyz_equation(self, ray: Ray, t: float) -> np.ndarray:
        x, y, z = ray.origin + ray.direction * t
        x = ((x + self.a/2) % self.a) - self.a/2
        y = ((y + self.b/2) % self.b) - self.b/2
        z = ((z + self.c/2) % self.c) - self.c/2
        return np.array([x, y, z])
    
    def get_intersection(self, ray: Ray, object: _IntersectableObject) -> float:
        return adaptive_step(ray, object, self)

    def get_intersections(self, ray: Ray,
                   objects: List[_IntersectableObject],
                   max_distance: float = float("inf")) -> Tuple[_IntersectableObject, np.ndarray]:
        intersected_object = None
        t_of_closest = float("inf")
        found_intersection = False
        max_t, max_t_direction = self._max_t(ray)

        for _ in range(int(self.repetitions)):
            for obj in objects:
                if hasattr(obj, "euclidean"): # Object ma izpeljano formulo k direkt vrne paremetr t
                    method = getattr(obj, "euclidean") 
                    t = method(ray)
                else:
                    t = self.get_intersection(ray.copy(), obj)
                
                if t is not None and t <= t_of_closest and t <= max_distance:
                    # Update the closest object, break
                    t_of_closest = t
                    intersected_object = obj
                    found_intersection = True
                
            # If we found an intersection, break
            if found_intersection:
                break
            else: 
                # Update the position, max_t for the next for iteration
                ray.origin = Euclidean.xyz_equation(Euclidean(), ray, max_t) # Nekje pasam in ray k bi ga mogu premaknt predn ga passam in!!!
                ray.origin[max_t_direction] = -ray.origin[max_t_direction] # Reflect
                max_t, max_t_direction = self._max_t(ray)

        if not intersected_object:
            return None, None
        
        # Calculate the intersection point in intersection was found
        intersection_point = Euclidean.xyz_equation(Euclidean(), ray, t_of_closest)
        return intersected_object, intersection_point
    
    def _max_t(self, ray: Ray) -> Tuple[float, int]:
        t = float("inf")
        min_t_in_direction = 0

        # Za x, y, z smer prever:
        for i in range(3):
            if ray.direction[i] > 0:
                new_t = (self.boundry_size[i]/2 - ray.origin[i]) / ray.direction[i]

                if new_t < t:
                    t = new_t
                    min_t_in_direction = i
            elif ray.direction[i] < 0:
                new_t = (-self.boundry_size[i]/2 - ray.origin[i]) / ray.direction[i] 

                if new_t < t:
                    t = new_t
                    min_t_in_direction = i

        # Samo če je position izven boundry boxa, se lahko zgodi da je t < 0 -> error!
        if t < 0:
            raise ValueError("t < 0 -> ray is going away from the boundry. Is camera inside the boundry?")
        
        return (t, min_t_in_direction)
SpacesRegistry.register("flattorus", FlatTorus, 
                              "FlatTorus space is like a normal space in a cube with sides (a, b, c) (in order x, y, z), and when a ray reaches one side it teleports to the other side.\n" + 
                              "      Usage: FlatTorus [boundry_size=(a, b, c)], [repetitions=10]")


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
    def xyz_equation(self, ray: Ray, t: float) -> np.ndarray: #TODO Tukej bi naredu memorizacijo, in u in v zračunu iz podanga raya ker (če kamera ne gleda naravnost) ta k je znotrej raya ni pravi.
        u, v = vector_uvw.vector_to_degrees(ray.direction)
        # u, v = ray.direction_deg[:2]
        vector_to_center = vector_uvw.degrees_to_vector((u, v - 90)) # Vektor ki gre od točke prot centru "sfere"
        sphere_center = ray.origin + vector_to_center * self.R # Za R proti središču sfere od točke na sferi je center

        u = np.radians(u)
        # t is already in radians

        x = self.R * np.cos(u) * np.cos(-t - np.pi/2) + sphere_center[0]
        y = self.R * np.sin(-t - np.pi/2) + sphere_center[1]
        z = self.R * np.sin(u) * np.cos(-t - np.pi/2) + sphere_center[2]
        return np.array([x, y, z])

    def get_intersection(self, ray: Ray, object: _IntersectableObject) -> float:
        return adaptive_step(ray, object, self, t0=0)
SpacesRegistry.register("twosphere", TwoSphere, 
                              "TwoSphere space is a space where rays travel on the surface of a sphere with radius R.\n" + 
                              "      Usage: TwoSphere [R=2]")
