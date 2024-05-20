# Vsebuje Space razrede, ki enkapsulirajo logiko specifično za vsak space.

import typehints as th
import numpy as np
import math

# Vsi space morjo bit otroci _Space classa, in povozt vse njen metode.

class _Space:
    def move(self, position: th.position, direction: th.direction , step) -> th.position:
        """Premakne ray ki se začne v točki position(x, y, z) za step_size v smeri direction(u, v, w)"""
        pass


class Euclidean(_Space):
    def move(self, position: th.position, direction: th.direction , step) -> th.position:
        x = position[0] + step * direction[0]
        y = position[1] + step * direction[1]
        z = position[2] + step * direction[2]
        return (x, y, z)

# Torus
class Torus(_Space):
    def move(self, position: th.position, direction: th.direction , step) -> th.position:
        pass

# 2-Sphere
class TwoSphere(_Space):
    # TODO: constructor 
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
