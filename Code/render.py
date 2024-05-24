# Kar mu je podano zrenderja.

from typing import List, Type
import numpy as np
import pygame

import typehints as th
from scene import Scene
from spaces import _Space, Euclidean, Torus, TwoSphere
from objects import _IntersectableObject, Light, Camera

import logging
logger = logging.getLogger(__name__)

class Renderer:
    
    def __init__(self, scene: Type[Scene], resolution: th.resolution = (800, 600)):
        self.scene = scene
        # TODO Resolution dj v render, tukej "save path" in save funkcija
        self.resolution = resolution # (width, height) 0-inf
    
    @property
    def resolution(self) -> th.resolution:
        return (self.resolution_x, self.resolution_y)
    
    @resolution.setter
    def resolution(self, resolution: th.resolution):
        self.resolution_x, self.resolution_y = resolution

    def render(self, step_size: float = 0.1, max_distance: float = 4.0, tolerance: float = 0.0001) -> np.ndarray:
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

        # Naredim nov image zadevo
        image = np.ndarray((res_x, res_y, 3), dtype=np.uint8)

        # Debug
        logger.info(f"Rendering scene {res_x}x{res_y} with fov {fov}.")
        logger.debug(f"""\n    Camera position: {camera.position}
    Camera direction: {camera.rotation}
    Initial ray direction deg: {ray_direction_deg}
    fov_x: {fov_x}, fov_y: {fov_y}
    kot_step: {kot_step}""")
        
        # Za izpis pikic: 
        print("|start..........................................................................................end|", )
        izpisanih_pikic = 0

        # Za vsak piksel v sliki
        for i in range(res_x):
            for j in range(res_y):
                ray_direction_vec = self._degrees_to_vector(ray_direction_deg)
                image[i, j] = self._trace_ray(camera.position, ray_direction_vec, max_distance, step_size, tolerance)

                # Vsak kot slike izpiše
                if j == 0 or j == res_y - 1:
                    if i == 0 or i == res_x - 1:
                        logger.debug(f"Ray {i} {j}: {ray_direction_vec}; {ray_direction_deg}")

                # Obrnem ray
                ray_direction_deg[1] -= kot_step
            # Obrnem ray
            ray_direction_deg[0] += kot_step
            ray_direction_deg[1] = fov_y/2

            # Izpis pikic
            if (i / res_x) * 100 > izpisanih_pikic:
                print(".", end="", flush=True)
                izpisanih_pikic += 1
        
        return image

    # HELPER FUNCTIONS

    def _trace_ray(self, position: np.ndarray, direction: np.ndarray, max_distance: float, step_size: float, tolerance: float) -> th.color: #TODO Should i use np arrays or tuples?
        """Traces ray, returns its color."""
        light: Light = self.scene.lights[0]
        space: _Space = self.scene.space

        # Find the intersection with the scene
        intersected_object, intersection_point = space.find_intersection(position, direction, max_distance, self.scene, step_size, tolerance)
        if not intersected_object:
            return (0, 0, 0) # Black
        
        # Does the pixel hit anything before the light?
        light_direction = np.array([light.pos_x - intersection_point[0], light.pos_y - intersection_point[1], light.pos_z - intersection_point[2]])
        light_distance = np.linalg.norm(light_direction)
        light_direction = light_direction / light_distance # Normalize

        # Check if the light is visible
        shadow_object, _ = space.find_intersection(intersection_point, light_direction, light_distance, self.scene, step_size, tolerance)
        if shadow_object:
            return (intersected_object.color_r // 4, intersected_object.color_g // 4, intersected_object.color_b // 4)
        
        # Return the object color
        return (intersected_object.color_r, intersected_object.color_g, intersected_object.color_b)

    @staticmethod
    def _vector_to_degrees(v: np.ndarray) -> tuple:
        """
        Convert a direction vector into angles in degrees (pan, tilt, 0).
        """
        # Normalize vector to avoid scale issues
        norm_v = v / np.linalg.norm(v)
        x, y, z = norm_v

        # Calculate tilt (assuming rotation around z-axis affects x and y)
        u = np.arctan2(z, x)  # Project on xy-plane and calculate angle
        u = np.degrees(u)  # Convert radians to degrees

        # Calculate pan (assuming rotation around y-axis affects x and z)
        v = np.arctan2(y, np.sqrt(x**2 + z**2))  # Rotate back from z to align with x-axis
        v = np.degrees(v)  # Convert radians to degrees

        # Convert radians to degrees
        return np.array([u, v, 0])

    @staticmethod
    def _degrees_to_vector(rotation: np.ndarray) -> np.ndarray:
        """
        Convert angles in degrees (pan, tilt, 0) to a direction base vector.
        """
        u, v, _ = rotation # (pan, tilt, roll), roll not used right now.

        # Convert degrees to radians
        u = np.radians(u)
        v = np.radians(v)

        x = np.cos(u) * np.cos(v)
        y = np.sin(v)
        z = np.sin(u) * np.cos(v)

        return np.array([x, y, z])

    @staticmethod
    def _get_rotation_matrix(rotation: np.ndarray) -> np.ndarray:
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

        # Rotation matrix around the z-axis (tilt) pitch 
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
