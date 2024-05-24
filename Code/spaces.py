# Vsebuje Space razrede, ki enkapsulirajo logiko specifično za vsak space.

import typehints as th
import numpy as np
import math
from typing import Tuple, List, Callable


from objects import _IntersectableObject

# Vsi space morjo bit otroci _Space classa, in povozt vse njen metode.

class _Space:
    name: str = "Pozabu si me preimenovat!"

    @staticmethod
    def find_intersection(position: np.ndarray, direction: np.ndarray, max_distance: float, scene: Callable, step_size: float, tollerance: float) -> Tuple[_IntersectableObject, th.position]:
        """Returns the first intersection of the ray with the scene.
        Args:
            position: The starting position of the ray.
            direction: The direction of the ray.
            step_size: The step size for the ray.
            max_distance: The maximum distance the ray can travel.
            objects: The objects in the scene.
        Returns:
            The point of intersection"""
        raise NotImplementedError
    

#
class Euclidean(_Space):

    def __init__(self):
        self.name = "Euclidean"
    
    @staticmethod
    def find_intersection(position: np.ndarray, direction: np.ndarray, max_distance: float, scene: Callable, step_size: float, tollerance: float) -> Tuple[_IntersectableObject, th.position]:
        objects: List[_IntersectableObject] = scene.objects

        current_position = np.array(position, dtype=np.float64) # Copy the position so we don't change the original
        current_position += direction * step_size * 2.0 # Move the position a bit forward to avoid self-intersection

        signs = {obj: obj.sign(current_position) for obj in objects}
        traveled_distance = step_size * 2 # count for self intersection correction
        intersected_object = None

        while step_size >= tollerance and traveled_distance <= max_distance: # Break if step size is too small or max distance is reached
            # Step forward
            current_position += direction * step_size
            traveled_distance += step_size

            # Check signs of all objects
            for obj in objects:
                current_sign = obj.sign(current_position)
                if current_sign != signs[obj]:
                    # Sign changed, halve the step size and step back
                    current_position -= direction * step_size
                    traveled_distance -= step_size
                    step_size *= 0.5
                    intersected_object = obj
                    break  # exit for loop

        return intersected_object, current_position  # Or return an appropriate result if an intersection is found

# Torus
class Torus(_Space):
    def __init__(self):
        self.name = "Flat Torus"
    def move(self, position: th.position, direction: th.direction , step) -> th.position:
        x = (position[0] + step * direction[0])%1
        y = (position[1] + step * direction[1])%1
        z = (position[2] + step * direction[2])%1
        return (x, y, z)

# 2-Sphere
class TwoSphere(_Space):

    def __init__(self):
        self.name = "2-Sphere"
    
    # TODO: meki macroti / settingsi
    radius = 2
    center: th.position

    def uvToVec(self, u: float, v:float) -> th.position:
        x = self.radius*math.cos(v)*math.sin(u)
        y = self.radius*math.sin(v)*math.sin(u)
        z = self.radius*math.cos(u)
        return (x, y, z)

    def sphereCenter(self, position: th.position, direction: th.direction) -> th.position:
        radius = 2
        # cross product straight down x direction d(ray) -> circle plane normal n
        n=np.cross([0,0,-1], direction)
        # cross product direction x normal -> a vector in circle plane perpendicular to ray
        C=np.cross(direction, n)
        # normalize and extend to length R ... C = center of 2-sphere
        C=np.add(np.multiply(np.divide(C, np.linalg.norm(C)), self.radius), position)
        return C

    def euler(self, y1: float, y2: float, y3: float, y4: float, h):
        y1n = y1 + h*y2
        y2n = y2 + h*math.cos(y1)*math.sin(y1)*(y4*y4)
        y3n = y3 + h*y4
        y4n = y4 + h*-2*(1/math.tan(y1))*y2*y4
        if(y1n == 0):
            h=h*2
            print("ha", h)
        return (y1n, y2n, y3n, y4n, h)

    def initializeState(self, position: th.position, direction: th.direction, h) -> tuple[float, float, float, float]:
        self.center = self.sphereCenter(position, direction)
        # move to 0, 0, 0
        T = np.subtract(position, self.center)

        # Initial parameters
        # u
        y1 = math.acos(T[2]/self.radius)
        if(y1==0):
            y1=0.1;
        # v
        y3 = math.atan2(T[1], T[0])
        # du
        y2=1
        # dv
        y4=0

        # Calculate first point approximation
        y1n, y2n, y3n, y4n, h = self.euler(y1, y2, y3, y4, h)
        D = np.subtract(np.add(self.uvToVec(y1n, y3n), self.center), position)

        # Dot product of vector towards first point and expected direction should be positive,
        # otherwise change direction (intial parameters)
        if(np.dot(direction, D) < 0):
            y2 = -1

        return (y1, y2, y3, y4)


    def move(self, state: tuple[float, float, float, float], h) -> tuple[tuple[float, float, float, float], int, th.position]:
        y1p = state[0]
        y2p = state[1]
        y3p = state[2]
        y4p = state[3]

        y1t, y2t, y3t, y4t, h = self.euler(y1p, y2p, y3p, y4p, h)
        x, y, z = np.add(self.uvToVec(y1t, y3t), self.center)

        return ((y1t, y2t, y3t, y4t), h, (x, y, z))
