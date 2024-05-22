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
    
    def __init__(self, scene: Type[Scene], resolution: th.resolution = (800, 600), background_color: th.color = (0, 0, 0)):
        self.scene = scene
        self.resolution = resolution # (width, height) 0-inf
        self.background_color = background_color
        pygame.init()
        pygame.display.set_caption("Raytracer")

    def render(self, step_size: float = 0.1, max_steps: int = 1000, tolerance: float = 0.01):
        """Renders the scene and returns the image."""

        # Par stvari nastavm
        camera: Type[Camera] = self.scene.cameras[0]
        cam_u, cam_v, cam_w = camera.rotation
        fov = camera.fov # Po diagonali

        resolution_x, resolution_y = self.resolution

        # Nastavm pygame
        
        screen = pygame.display.set_mode((resolution_x, resolution_y))
        screen.fill(self.background_color)

        # Zračunam kot med diagonalo slike glede na razmerje med širino in višino
        kot = np.arctan(resolution_x / resolution_y)
        fov_x = np.sin(kot) * fov
        fov_y = np.cos(kot) * fov

        # Step size kota v x in y smeri
        kot_step = fov_x / resolution_x # Dejansko sta enaka, ker je piksel kvadraten.

        # Initial smer raya zračunam kot polovica fov_x lavo in fov_y gor
        ray_direction = np.array([cam_u - (fov_x / 2), 
                                  cam_v - (fov_y / 2),
                                  cam_w])

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
                direction_vector = self.degrees_to_vector(ray_direction)
                ray = _Ray(camera.position, direction_vector)
                color = self._trace_ray(ray)
                
                # Debug
                if j == 0 or j == resolution_y - 1: 
                    if i == 0 or i == resolution_x - 1:
                        logger.debug(f"Pixel ({i}, {j}) direction: {ray_direction}, vector: {direction_vector}, color: {color}")

                # Narišem pixel
                screen.set_at((i, j), color)

                # Premik v vertikalni smeri
                ray_direction[1] -= kot_step

            # Premaknem ray v horizontalni smeri + premik višine na začetk
            ray_direction[0] += kot_step
            ray_direction[1] = cam_v - (fov_y / 2) # Resetiram višino
    
    def show_image(self):
        """Shows the rendered image."""
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    def save_image(self, filename: str = "render.png"): 
        pass

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
                    stateCurrent = self.space.initializeState(ray.position, ray.direction, h)
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

    # HELPER FUNCTIONS

    def degrees_to_vector(self, rotation: th.rotation) -> np.ndarray:
        """
        Convert angles in degrees (tilt, roll, pan) to a direction base vector.

        Args:
            rotation (tuple[float, float, float]): A tuple of three angles in degrees (pan, tilt, roll).

        Returns:
            np.ndarray: A 3D direction vector.
        """
        pan, tilt, roll = rotation

        # Convert degrees to radians
        tilt_rad = np.radians(tilt)
        roll_rad = np.radians(roll)
        pan_rad = np.radians(pan)

        # Rotation matrix around the y-axis (pan)
        R_y = np.array([
            [np.cos(pan_rad), 0, -np.sin(pan_rad)],
            [0, 1, 0],
            [np.sin(pan_rad), 0, np.cos(pan_rad)]
        ])

        # Rotation matrix around the z-axis (tilt)
        R_z = np.array([
            [np.cos(tilt_rad), -np.sin(tilt_rad), 0],
            [np.sin(tilt_rad), np.cos(tilt_rad), 0],
            [0, 0, 1]
        ])

        # Rotation matrix around the x-axis (roll)
        R_x = np.array([
            [1, 0, 0],
            [0, np.cos(roll_rad), -np.sin(roll_rad)],
            [0, np.sin(roll_rad), np.cos(roll_rad)]
        ])

        # Combined rotation matrix
        R = np.dot(np.dot(R_x, R_y), R_z)

        # Initial direction vector (assuming forward direction along the z-axis)
        initial_vector = np.array([1, 0, 0]) # (x, y, z)

        # Apply the rotation matrix to the initial vector
        direction_vector = np.dot(R, initial_vector)

        return direction_vector