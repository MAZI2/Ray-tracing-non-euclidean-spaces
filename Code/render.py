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
    
    def __init__(self, scene: Type[Scene], resolution: th.resolution = (800, 600)):
        self.scene = scene
        self.resolution = resolution # (width, height) 0-inf
    
    @property
    def resolution(self) -> th.resolution:
        return (self.resolution_x, self.resolution_y)
    
    @resolution.setter
    def resolution(self, resolution: th.resolution):
        self.resolution_x, self.resolution_y = resolution

    def render(self, step_size: float = 0.1, max_steps: int = 1000, tolerance: float = 0.01) -> np.ndarray:
        """Renders the scene and returns the image."""

        # Par stvari nastavm
        camera: Type[Camera] = self.scene.cameras[0]
        cam_u, cam_v, cam_w = camera.rotation
        fov = camera.fov # Po diagonali

        res_x, res_y = self.resolution

        # Zračunam kot med diagonalo slike glede na razmerje med širino in višino
        kot = np.arctan(res_x / res_y) # Kot med diagonalo in širino "slike"
        fov_x = np.sin(kot) * fov
        fov_y = np.cos(kot) * fov

        # Step size kota v x in y smeri
        kot_step = fov_x / res_x # Dejansko sta enaka, ker je piksel kvadraten.

        # Initial smer raya zračunam kot polovica fov_x lavo in fov_y gor
        ray_direction_deg = np.array([cam_u - (fov_x / 2), 
                                  cam_v + (fov_y / 2),
                                  cam_w])
        ray_direction = self._degrees_to_vector(ray_direction_deg) # Initial direction vector
        
        # Create the rotation matrices for rotating the ray direction
        rot_down_step = self._get_rotation_matrix((0, -kot_step, 0))
        rot_up_right_fov = self._get_rotation_matrix((kot_step, fov_y, 0))

        # Naredim nov image zadevo
        image = np.zeros((res_x, res_y, 3), dtype=np.uint8)

        logger.info(f"Rendering scene {res_x}x{res_y} with fov {fov}.")
        logger.debug(f"""\n    Camera position: {camera.position}
    Camera direction: {camera.rotation}
    Initial ray direction deg: {ray_direction_deg}; vector: {ray_direction}
    fov_x: {fov_x}, fov_y: {fov_y}
    kot_step: {kot_step}
    rot_down_step matrix: {rot_down_step}, rot_up_right_fov matrix: {rot_up_right_fov}""")
        
        # Za pzpis pikic: 
        print("|start..........................................................................................end|", )

        # Za vsak pixel en ray, narišem na pygame
        for i in range(res_y):
            for j in range(res_x):
                pass
                # Zračunam ray
                color = self._trace_ray(camera.position, ray_direction)

                # Debug
                # if j == 0 or j == res_x - 1: 
                #     if i == 0 or i == res_y - 1:
                #         logger.debug(f"Pixel ({i}, {j}) vector: {ray_direction}, color: {color}")

                # Obrnem ray
                ray_direction = np.dot(rot_down_step, ray_direction)
                
                # Narišem pixel
                image[j, i] = [255, 0, 255]

            # Premaknem ray v horizontalni smeri + premik višine na začetk
            ray_direction = np.dot(rot_up_right_fov, ray_direction)

            # Izpis pikic
            if i % (res_y // 100) == 0:
                print(".", end="", flush=True)
                

        return image

    # HELPER FUNCTIONS

    def _trace_ray(self, position: th.position, direction: th.direction) -> th.color:
        """Traces the ray through the scene and returns the color of the pixel."""
        # Za debug return random
        # return (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        return (255, 0, 255)

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

    @staticmethod
    def _get_rotation_matrix(rotation: th.rotation) -> np.ndarray:
        """
        Convert angles in degrees (tilt, roll, pan) to matrix that returns a direction vector.
        R v = v'

        Args:
            rotation (tuple[float, float, float]): A tuple of three angles in degrees (pan, tilt, roll).

        Usage exampole:
            rotation_matrix = self._get_rotation_matrix((0, 0, -90))
            ray_direction = np.dot(rotation_matrix, np.array([1, 0, 0]))
        Returns:
            np.ndarray: A 3x3 rotation matrix.
        """
        pan, tilt, roll = rotation

        # Convert degrees to radians
        tilt_rad = np.radians(tilt)
        roll_rad = np.radians(roll)
        pan_rad = np.radians(pan)

        # Rotation matrix around the y-axis (pan) yaw
        R_y = np.array([
            [np.cos(pan_rad), 0, -np.sin(pan_rad)],
            [0, 1, 0],
            [np.sin(pan_rad), 0, np.cos(pan_rad)]
        ])

        # Rotation matrix around the z-axis (pitch)
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
        return np.dot(np.dot(R_x, R_z), R_y)

    @staticmethod
    def _degrees_to_vector(rotation: th.rotation) -> np.ndarray:
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
        R = np.dot(np.dot(R_x, R_z), R_y)

        # Initial direction vector (assuming forward direction along the z-axis)
        initial_vector = np.array([1, 0, 0]) # (x, y, z)

        # Apply the rotation matrix to the initial vector
        direction_vector = np.dot(R, initial_vector)

        return direction_vector
