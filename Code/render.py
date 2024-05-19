# Kar mu je podano zrenderja.

from typing import List, Type

import typehints as th
from spaces import _Space
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

    def render(self, step_size: float = 0.01, max_steps: int = 1000):
        """Renders the scene and returns the image."""
        # Iz kamere zračuna kote rayev
        # Za vsak pixel v resoluciji požene ray z _traceray, in ki vrne barvo
        # Barvo shrani v image, returna image.
        pass

    def _trace_ray(self, ray: _Ray):
        """Traces the ray through the scene and returns the color of the pixel."""
        # Kje se ray interescta
        # Zračnaš smer intersection - luč
        # Poženeš intersection do luči, če kje intersecta pol je in shadow (temna) sicer svetla.
        pass

    def _intersection(self, ray: _Ray, step_size: float, max_steps: int) -> th.position:
        """Returns the first intersection of the ray with the scene."""
        # Rekurzivno se kliče, vsak klic prever za vsak objekt v sceni če se je spremenil predznak
        # Če se je, najde točn intersection z uno metodo in vrne točko.

        # t ... number of steps 1->max_steps 
        prev_position = ray.position
        for t in range(1, max_steps):
            new_position = 0 
            # euclidean
            
            # flat torus

            # 2-sphere
            if (type(self.space) == Euclidean):
                new_position = self.space.move(ray.position, ray.direction, t)

            sign_index = 0
            # TODO: mormo pazit da uredu razporedimo objekte, ker cene lahko spremeni 
            # predznak za vec objektov v eni iteraciji, vrne pa samo eno presecisce
            for obj in objects:
                if len(signs) < len(objects):
                    signs.append(obj.sign(new_position))
                else:
                    if signs[sign_index] != obj.sign(new_position):
                        # TODO: intersection = gaussNewtonIteration((new_position + prev_position)/2)
                        # return intersection

                sign_index += 1
            prev_position = new_position

        pass

