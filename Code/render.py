# Kar mu je podano zrenderja.

from typing import List, Type
import numpy as np
import pygame

import typehints as th
from scene import Scene
from spaces import _Space, Euclidean, Torus, TwoSphere
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

    def render(self, step_size: float = 0.1, max_steps: int = 1000, tolerance: float = 0.01):
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

