# Kar mu je podano zrenderja.

from typing import List, Type
import numpy as np
import pygame

import typehints as th
from scene import Scene
from objects import _Scene_object, Light, Camera

import logging
logger = logging.getLogger(__name__)

class _Ray:
    position: th.position
    direction: th.rotation

    def __init__(self, position: th.position, direction: th.rotation):
        self.position = position
        self.direction = direction

class Renderer:
    scene: Type[Scene]
    background_color: th.color = (0, 0, 0)
    
    def __init__(self, scene: Type[Scene]):
        self.scene = scene
        pygame.init()

    def render(self, step_size: float = 0.01, max_steps: int = 1000):
        """Renders the scene and returns the image."""

        # Par stvari za kamero
        camera: Type[Camera] = self.scene.camera
        cam_direction = camera.rotation
        resolution_x = camera.resolution[0] # Horizontalna
        resolution_y = camera.resolution[1] # Vertikalna
        fov = camera.fov # Po diagonali

        # Nastavm pygame
        pygame.display.set_caption("Raytracer")
        screen = pygame.display.set_mode((resolution_x, resolution_y))
        screen.fill(self.background_color)

        # Zračunam kot med diagonalo slike glede na razmerje med širino in višino
        kot = np.arctan(camera.resolution[0] / camera.resolution[1])
        fov_x = np.sin(kot) * fov
        fov_y = np.cos(kot) * fov

        # Step size kota v x in y smeri
        kot_step = fov_x / resolution_x # Dejansko sta enaka, ker je piksel kvadraten.

        # Initial smer raya zračunam kot polovica fov_x lavo in fov_y gor
        ray_direction = (cam_direction[0] - (fov_x / 2), 
                         cam_direction[1], # Obračanje okoli x osi nespremenjeno
                         cam_direction[2] + (fov_y / 2))

        logger.info(f"Rendering scene {resolution_x}x{resolution_y} with fov {fov}.")
        logger.debug(f"""\n    Camera position: {camera.position}
    Camera direction: {camera.rotation}    
    Initial ray direction: {ray_direction}
    fov_x: {fov_x}, fov_y: {fov_y}
    kot_step: {kot_step}""")

        
        # Za vsak pixel en ray, narišem na pygame
        for i in range(resolution_x):
            for j in range(resolution_y):
                # Zračunam ray
                ray = _Ray(camera.position, ray_direction)
                color = self._trace_ray(ray)

                # Narišem pixel
                screen.set_at((i, j), color)

                # Premik v vertikalni smeri
                ray_direction = (ray_direction[0], ray_direction[1], ray_direction[2] - kot_step)

            # Premaknem ray v horizontalni smeri + premik višine na začetk
            ray_direction = (ray_direction[0] + kot_step, ray_direction[1], ray_direction[2] + fov_y)
        
        logger.debug("Rendering finished.")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()

        pygame.quit()

            


    def _trace_ray(self, ray: _Ray):
        """Traces the ray through the scene and returns the color of the pixel."""
        # Za debug return random
        return (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))

    # def _intersection(self, ray: _Ray, step_size: float, max_steps: int) -> th.position:
    #     """Returns the first intersection of the ray with the scene."""
    #     # Rekurzivno se kliče, vsak klic prever za vsak objekt v sceni če se je spremenil predznak
    #     # Če se je, najde točn intersection z uno metodo in vrne točko.

    #     # t ... number of steps 1->max_steps 
    #     prev_position = ray.position
    #     for t in range(1, max_steps):
    #         new_position = 0 
    #         # euclidean
            
    #         # flat torus

    #         # 2-sphere
    #         if (type(self.space) == Euclidean):
    #             new_position = self.space.move(ray.position, ray.direction, t)

    #         sign_index = 0
    #         # TODO: mormo pazit da uredu razporedimo objekte, ker cene lahko spremeni 
    #         # predznak za vec objektov v eni iteraciji, vrne pa samo eno presecisce
    #         for obj in objects:
    #             if len(signs) < len(objects):
    #                 signs.append(obj.sign(new_position))
    #             else:
    #                 if signs[sign_index] != obj.sign(new_position):
    #                     # TODO: intersection = gaussNewtonIteration((new_position + prev_position)/2)
    #                     # return intersection

    #             sign_index += 1
    #         prev_position = new_position

    #     pass
    
