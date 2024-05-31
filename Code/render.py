# Kar mu je podano zrenderja.

from typing import List, Type, Callable, Tuple
import numpy as np
import multiprocessing
import time

import typehints as th
from scene import Scene
from spaces import _Space, Euclidean
from objects import _IntersectableObject, Light, Camera
from ui import UI
from utilities import  vector_uvw, Ray, Timer, Logger
from methods import broyden


class _RendererWorker:
    def __init__(self, logger_name: str = "_RendererWorker"):
        self.logger = Logger.setup_logger(logger_name)
    
    def run(self, column_num: int, 
            res_y: int, 
            kot_step: float, 
            ray_origin: np.ndarray,
            ray_direction_deg: np.ndarray,
            objects: List[_IntersectableObject], 
            lights: List[Light], 
            space: _Space, 
            background_color: np.ndarray = np.array([0, 0, 0])) -> Tuple[np.ndarray, int]:
        """Renders a single line of the image."""
        image = np.ndarray((res_y, 3), dtype=np.uint8)

        # For each pixel in the column
        for j in range(res_y):
            true_ray_direction_deg = [ray_direction_deg[0]/np.cos(np.radians(ray_direction_deg[1])), ray_direction_deg[1]]
            ray_direction_vec = vector_uvw.degrees_to_vector(true_ray_direction_deg)
            ray = Ray(ray_origin, ray_direction_vec, ray_direction_deg)
            
            image[j] = self._trace_ray(ray, objects, lights, space, background_color)

            # Obrnem ray
            ray_direction_deg[1] -= kot_step
            # if ray_direction_deg[1] < -90:
            #     odmik = ray_direction_deg[1] + 90
            #     ray_direction_deg[1] = -90 - odmik
            #     ray_direction_deg[0] += 180 if ray_direction_deg[0] < 0 else -180
            #     kot_step = -kot_step
        
        self.logger.debug(f"Column {column_num} rendered.")

        return image, column_num
    
    def _trace_ray(self, ray: Ray, 
                  objects: List[_IntersectableObject], 
                  lights: List[Light],
                  space: _Space,
                  background_color: np.ndarray) -> np.ndarray:
        """Traces ray, returns its color."""
        light: Light =lights[0]
        

        # Find the intersection with the scene
        intersected_object, intersection_point = self._find_intersection(ray, objects, space)
        if not intersected_object:
            return background_color # Black
        
        # Does the pixel hit anything before the light?
        light_direction = np.array([light.x - intersection_point[0], 
                                    light.y - intersection_point[1], 
                                    light.z - intersection_point[2]])
        light_distance = np.linalg.norm(light_direction)
        light_direction = light_direction / light_distance # Normalize

        # Check if the light is visible
        new_ray = Ray(intersection_point, light_direction)
        shadow_object, _ = self._find_intersection(new_ray, objects, Euclidean(), light_distance)
        if shadow_object:
            r, g, b = intersected_object.rgb
            return (r // 4, g // 4, b // 4)
        
        # Return the object color
        return intersected_object.rgb
    
    def _find_intersection(self, ray: Ray,
                          objects: List[_IntersectableObject],
                          space: _Space,
                          max_distance: float = float("inf")) -> Tuple[_IntersectableObject, np.ndarray]:
        """Finds closest intersection of ray with scene using eather izpeljane formule k jih maš v objektih napisane
        or sekantna metoda. Če ma space get_intersections funkcijo samo kličem tisto."""
        space_name: str = space.name

        # If a space implements its own intersection function, use that
        if hasattr(space, "get_intersections") and space.get_intersections(ray.copy(), list(), float("inf")) != -1:
            return space.get_intersections(ray.copy(), objects, max_distance)
        
        # Else this is the default intersection function:
        intersected_object = None
        t_of_closest = float("inf")

        # What object get_intersectionst closest?
        for obj in objects:
            if hasattr(obj, space_name): # Object ma izpeljano formulo k direkt vrne paremetr t
                method = getattr(obj, space_name) 
                t = method(ray)
            else:
                t = space.get_intersection(ray.copy(), obj)

            if t is not None and t <= t_of_closest and t <= max_distance:
                t_of_closest = t
                intersected_object = obj

        # Calculate the intersection point
        if intersected_object:
            intersection_point = space.xyz_equation(ray, t_of_closest)
            return intersected_object, intersection_point
        else:
            return None, None


class Renderer:
    def __init__(self):
        self.pool = multiprocessing.Pool(processes=multiprocessing.cpu_count(),
                                         initializer=Renderer.init_worker,
                                         initargs=('_RendererWorker', ))
        self.manager = multiprocessing.Manager()
        self.lock = self.manager.Lock()

        self.init_worker("_Renderer") # For the main thread

        self.logger = Logger.setup_logger("Renderer")
        self.logger.info("Renderer initialized.")
        # za merjenje časa renderiranja
        self.timer = Timer()
        self.num_recieved_rows = 0

    def  __del__(self):
        self.logger.info("Closing the pool, exiting renderer.")
        self.pool.close()
        self.pool.join()

    @staticmethod
    def init_worker(logger_name: str):
        global worker 
        worker = _RendererWorker(logger_name)
    
    # Rendering
    def render(self, scene: Scene, 
               resolution: th.resolution = None,
               parallel: bool = True,
               background_color: np.ndarray = np.array([0, 0, 0], dtype=np.int8)):
        """Renders the scene and returns the image."""
        # Get camera:
        camera: Type[Camera] = scene.cameras[0]

        # Set resolution
        if resolution is not None:
            resolution = (int(resolution[0]), int(resolution[1]))
            camera.resolution = resolution # Set the resolution in the camera
        else:
            resolution = camera.resolution # Get the resolution from the camera
        
        # Set the resolution in the UI (and reset the frame)
        UI.reset_image(resolution)

        # Par stvari si vn dobim
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
                             cam_v + (fov_y / 2)])

        # Print and debug
        print("|start..........................................................................................end|")
        self.logger.debug(f"""\n    Camera position: {camera.position}
    Camera direction: {camera.orientation}
    Initial ray direction deg: {ray_direction_deg}
    fov_x: {fov_x}, fov_y: {fov_y}
    kot_step: {kot_step}""")

        # Merjenje časa in izpis pikic
        self.timer.start()
        self.num_recieved_rows = 0
        printed_dots = 0

        # za vsak stolpec
        for i in range(res_x):
            if parallel:
                self.pool.apply_async(worker.run, 
                                      args=(i, res_y, kot_step, camera.position, ray_direction_deg.copy(), 
                                            scene.objects, scene.lights, scene.space, background_color),
                                      callback=lambda result: self._recieve_column(*result))
            else:
                column, new_i = worker.run(i, res_y, kot_step, camera.position, ray_direction_deg.copy(), 
                                                    scene.objects, scene.lights, scene.space, background_color)
                self._recieve_column(column, new_i)

                # Izpis pikic not parralel:
                if (i / res_x) > printed_dots / 100:
                    printed_dots += 1
                    print(".", end="", flush=True)
            
            # Obrnem ray
            ray_direction_deg[0] += kot_step
        
        # Izpisovanje pikic za paralelno
        while self.num_recieved_rows < res_x:
            time.sleep(0.001)
            if (self.num_recieved_rows / res_x) > printed_dots / 100:
                printed_dots += 1
                print(".", end="", flush=True)
        
        # Čas in izpis pikic
        render_time = self.timer.stop()
        print(f"\nRendered in {render_time:.2f} seconds.")
        self.logger.debug(f"Rendered in {render_time:.2f} seconds.")
    
    def render_sync(self, scene: Scene, 
                    resolution: th.resolution = None,
                    background_color: np.ndarray = np.array([0, 0, 0], dtype=np.int8)):
        self.render(scene, resolution, parallel=False, background_color=background_color)

    # Plotting
    def plot(self, scene: Scene, name: str, pixel: Tuple[int, int] = None, from_t: float = 0, to_t: float = 10, space: _Space = None):
        camera: Type[Camera] = scene.cameras[0]
        space = space if space else scene.space
        object: _IntersectableObject = scene.get_scene_content(name)
        if object is None:
            raise ValueError(f"Object with name {name} not found in the scene.")

        # Če je podan i, j pol plotam ij-ti pixel, sicer v smer kamere (centr)
        if pixel is not None:
            resolution = camera.resolution # Get the resolution from the camera

            # Par stvari si vn dobim
            cam_u, cam_v, _ = camera.orientation
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
                                cam_v + (fov_y / 2)])

            # Obrnem ray tko kot praujo
            ray_direction_deg[0] += kot_step * pixel[1] # pixel(vrsta, stolpec)
            ray_direction_deg[1] -= kot_step * pixel[0]


            ray_direction_vec = vector_uvw.degrees_to_vector(ray_direction_deg)

            direction_vector = vector_uvw.degrees_to_vector(camera.orientation[:2])
            ray = Ray(camera.position, ray_direction_vec, ray_direction_deg)
        else:
            direction_vector = vector_uvw.degrees_to_vector(camera.orientation[:2])
            ray = Ray(camera.position, direction_vector, camera.orientation[:2])

        # Get the x values
        t_values = np.linspace(from_t, to_t, 1000)

        # Get the y values
        dist_values = np.array([object.equation(space.xyz_equation(ray, t)) for t in t_values])

        # Plot
        UI.plot(t_values, dist_values)
        


    # Helper functions
    def _recieve_column(self, column: np.ndarray, column_num: int):
        with self.lock:
            self.num_recieved_rows += 1
            UI.set_column(column, column_num)




















# Old code
    # @staticmethod
    # def find_intersection_with_steps(position: np.ndarray, 
    #                            direction: np.ndarray, 
    #                            max_distance: float, 
    #                            scene: Callable, 
    #                            step_size: float, 
    #                            tollerance: float) -> Tuple[_IntersectableObject, th.position]:
    #     objects: List[_IntersectableObject] = scene.objects

    #     current_position = np.array(position, dtype=np.float64) # Copy the position so we don't change the original
    #     current_position += direction * step_size * 2.0 # Move the position a bit forward to avoid self-intersection

    #     signs = {obj: obj.sign(current_position) for obj in objects}
    #     traveled_distance = step_size * 2 # count for self intersection correction
    #     intersected_object = None

    #     while step_size >= tollerance and traveled_distance <= max_distance: # Break if step size is too small or max t is reached
    #         # Step forward
    #         current_position += direction * step_size
    #         traveled_distance += step_size

    #         # Check signs of all objects
    #         for obj in objects:
    #             current_sign = obj.sign(current_position)
    #             if current_sign != signs[obj]:
    #                 # Sign changed, halve the step size and step back
    #                 current_position -= direction * step_size
    #                 traveled_distance -= step_size
    #                 step_size *= 0.5
    #                 intersected_object = obj
    #                 break  # exit for loop

    #     return intersected_object, current_position  # Or return an appropriate result if an intersection is found
