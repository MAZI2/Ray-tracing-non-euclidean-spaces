# Kar mu je podano zrenderja.

from typing import List, Type, Callable, Tuple
import numpy as np
import pygame
import time

import typehints as th
from scene import Scene
from spaces import _Space, Euclidean, FlatTorus, TwoSphere
from objects import _IntersectableObject, Light, Camera
from utilities import vector_uvw

import logging
logger = logging.getLogger(__name__)

class Renderer:
    
    def __init__(self, scene: Type[Scene]):
        self.scene = scene

    def render(self, resolution: th.resolution = (320, 240)) -> np.ndarray:
        """Renders the scene and returns the image."""

        # Par stvari nastavm
        camera: Type[Camera] = self.scene.cameras[0]
        cam_u, cam_v, cam_w = camera.orientation
        fov = camera.fov # Po diagonali

        res_x, res_y = resolution

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
    Camera direction: {camera.orientation}
    Initial ray direction deg: {ray_direction_deg}
    fov_x: {fov_x}, fov_y: {fov_y}
    kot_step: {kot_step}""")
        
        # Za izpis pikic: 
        print("|start..........................................................................................end|", )
        izpisanih_pikic = 0

        # Merjenje časa
        srart = time.time()

        # Za vsak piksel v sliki
        for i in range(res_x):
            for j in range(res_y):
                ray_direction_vec = vector_uvw.degrees_to_vector(ray_direction_deg)
                image[i, j] = self._trace_ray(camera.position, ray_direction_vec)

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

        end = time.time()
        logger.info(f"Rendering took {end - srart} seconds.")
        return image


    # Tracing rays functions
    def _trace_ray(self, position: np.ndarray, direction: np.ndarray) -> np.ndarray:
        """Traces ray, returns its color."""
        light: Light = self.scene.lights[0]
        space: _Space = self.scene.space
        

        # Find the intersection with the scene
        intersected_object, intersection_point = self.find_intersection(position, direction)
        if not intersected_object:
            return (0, 0, 0) # Black
        
        # Does the pixel hit anything before the light?
        light_direction = np.array([light.x - intersection_point[0], 
                                    light.y - intersection_point[1], 
                                    light.z - intersection_point[2]])
        light_distance = np.linalg.norm(light_direction)
        light_direction = light_direction / light_distance # Normalize

        # Check if the light is visible
        shadow_object, _ = self.find_intersection(intersection_point, light_direction, light_distance, Euclidean())
        if shadow_object:
            r, g, b = intersected_object.rgb
            return (r // 4, g // 4, b // 4)
        
        # Return the object color
        return intersected_object.rgb

    def find_intersection(self, position: np.ndarray, 
                          direction: np.ndarray,
                          max_distance: float = float("inf"),
                          space = None) -> Tuple[_IntersectableObject, th.position]:
        if not space: space: Type[_Space] = self.scene.space
        
        objects: List[_IntersectableObject] = self.scene.objects
        space_name: str = space.name
        cur_position = np.array(position, dtype=np.float64) # Copy the position so we don't change the original

        # If a space implements its own intersection function, use that
        if hasattr(space, "intersects") and space.intersects(np.array([0, 0, 0]), np.array([1, 0, 0]),
                                                             list(), float("inf")) != -1:
            return space.intersects(position, direction, objects, max_distance)
        
        # Else this is the default intersection function:
        intersected_object = None
        closest_distance = float("inf")

        # What object intersectst closest?
        for obj in objects:
            if hasattr(obj, space_name):
                method = getattr(obj, space_name)
                distance = method(cur_position, direction)
            else:
                # TODO Sekantna metoda
                pass
            if distance is not None and distance <= closest_distance and distance <= max_distance:
                closest_distance = distance
                intersected_object = obj

        # Calculate the intersection point
        intersection_point = cur_position + direction * closest_distance

        return intersected_object, intersection_point

        # If object has a function with the same name as the space, use that to get t
        if hasattr(self.scene.space, "intersects"):
            return self.scene.space.intersects(position, direction, objects, max_distance)



















    @staticmethod
    def find_intersection_with_steps(position: np.ndarray, 
                               direction: np.ndarray, 
                               max_distance: float, 
                               scene: Callable, 
                               step_size: float, 
                               tollerance: float) -> Tuple[_IntersectableObject, th.position]:
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
