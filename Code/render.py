# Kar mu je podano zrenderja.

from typing import List, Type

import typehints as th
import numpy as np
from spaces import _Space, Euclidean, Torus, TwoSphere
from objects import _Object, Light, Camera


class _Ray:
    starting_position: th.position
    direction: th.rotation
    # id: th.resolution # Mislm da sploh ne rabmo tega

    def __init__(self, starting_position: th.position, direction: th.rotation):
        self.starting_position = starting_position
        self.direction = direction

class Renderer:
    space: Type[_Space]
    objects: List[Type[_Object]]
    lights: Light
    camera: Camera
    signs: List[int]
    
    def __init__(self, space, objects, lights, camera):
        self.space = space
        self.objects = objects
        self.lights = lights
        self.camera = camera
        self.signs = list()

    def render(self, step_size: float = 0.1, max_steps: int = 1000, tolerance: float = 0.01):
        """Renders the scene and returns the image."""
        # Iz kamere zračuna kote rayev
        # Za vsak pixel v resoluciji požene ray z _traceray, in ki vrne barvo
        # Barvo shrani v image, returna image.


        """ Testing
        ray1 = _Ray((0, 0, 1), (1, 0, 0))
        ray2 = _Ray((0, 0, 1), (1, 0, 1))
        ray3 = _Ray((0, 0, 1), (1, 1, 1))
        ray4 = _Ray((0, 0, 1), (1, -1, -1))

        print(self._intersection(ray1, step_size, max_steps, tolerance))
        print(self._intersection(ray2, step_size, max_steps, tolerance))
        print(self._intersection(ray3, step_size, max_steps, tolerance))
        print(self._intersection(ray4, step_size, max_steps, tolerance))
        """

        pass

    def _trace_ray(self, ray: _Ray):
        """Traces the ray through the scene and returns the color of the pixel."""
        # Kje se ray interescta
        # Zračnaš smer intersection - luč
        # Poženeš intersection do luči, če kje intersecta pol je in shadow (temna) sicer svetla.
        pass

    def _intersection(self, ray: _Ray, step_size: float, max_steps: int, tolerance: float) -> tuple[th.position, Type[_Object]]:
        """Returns the first intersection of the ray with the scene."""
        # Prever za vsak objekt v sceni če se je spremenil predznak
        # Če se je, najde točn intersection z uno metodo in vrne točko.

        h = step_size;

        sign_index = 0
        signs = list()
        for obj in self.objects:
            signs.append(obj.sign(ray.starting_position))
            sign_index += 1

        TCurrent = ray.starting_position;
        TNew = TCurrent;

        stateNew = ();
        stateCurrent = ();

        step = 0;
        while(True):
            if(step == max_steps):
                break

            for obj in self.objects:
                if(np.absolute(obj.dist(TCurrent)) < tolerance):
                    return (TCurrent, obj)

            # Premik za step size h. Shrani novo tocko in stanje (parametri t, u, v, dv, du, ... karkoli potrebuje tvoj space) 
            # Za Euclidean / Flat torus lahko v state hranimo trenutni parameter t   (v = v0 + t*direction)
            # Lahko tudi zacetno tocko in direction

            if(type(self.space) == Euclidean):
                # TODO: Euclidean
                # stateNew, TNew = self.space.move(stateCurrent, h)
                print("Euclidean")

            elif(type(self.space) == Torus):
                # TODO: Torus
                # podobno
                print("Torus")

            elif(type(self.space) == TwoSphere):
                # 2-Sphere
                if(step == 0):
                    stateCurrent = self.space.initializeState(ray.starting_position, ray.direction, h)
                stateNew, h, TNew = self.space.move(stateCurrent, h)

            ix = 0
            changed = 0
            for obj in self.objects:
                if(obj.sign(TNew) != signs[ix]):
                    h = h/2
                    changed = 1
                    break
                ix += 1

            if(changed != 1):
                stateCurrent = stateNew
                TCurrent = TNew;
            step = step+1;

        return ()

