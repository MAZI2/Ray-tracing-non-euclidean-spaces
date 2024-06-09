# Imports
import queue
import numpy as np
import time
from typing import Tuple
import matplotlib.pyplot as plt
from utilities import suppress_stdout, Logger

with suppress_stdout():
    import pygame


class _UIEvents:
    quit = "quit"
    set_image = "set_image"
    set_column = "set_column"
    set_resolution = "set_resolution"
    plot = "plot"
    set_scale = "set_scale"
    reset_image = "reset_image"

_ui_command_queue = queue.Queue()

class UI:
    """Events that can be sent to the UI thread."""
    # Send events

    @staticmethod
    def set_image(image: np.ndarray):
        _ui_command_queue.put((_UIEvents.set_image, (image)))

    @staticmethod
    def set_resolution(resolution: Tuple[int, int]):
        _ui_command_queue.put((_UIEvents.set_resolution, (resolution)))

    @staticmethod
    def reset_image(resolution: Tuple[int, int]):
        _ui_command_queue.put((_UIEvents.reset_image, (resolution)))
    
    @staticmethod
    def set_column(column: np.ndarray, column_num: int):
        _ui_command_queue.put((_UIEvents.set_column, (column, column_num)))

    @staticmethod
    def plot(t_values: np.ndarray, dist_values: np.ndarray):
        _ui_command_queue.put((_UIEvents.plot, (t_values, dist_values)))

    @staticmethod
    def set_scale(scale: int):
        _ui_command_queue.put((_UIEvents.set_scale, scale))
    
    @staticmethod
    def stop_thread():
        _ui_command_queue.put(_UIEvents.quit)


class _UIThread():
    """MUST BE RUN ON MAIN THREAD
    This class is responsible for the UI thread. It is used to display the rendered image."""
    scale = 1

    @classmethod
    def configure(cls, scale: int):
        cls.scale = scale

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Raytracer")
        self.image = None # (res_x, res_y, 3)
        self.display = None
        self.display_initialized = False

        self.logger = Logger.setup_logger("_UIThread")
        self.logger.info("UI thread started.")

    def __del__(self):
        self.stop()
    
    # Main loop
    def ui_loop(self):
        running = True
        while running:
            # Check for UI events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    UI.stop_thread()
                    running = False
            
            # Execute the commands
            while not _ui_command_queue.empty():
                task = _ui_command_queue.get_nowait()
                if task == _UIEvents.quit:
                    running = False
                elif task[0] == _UIEvents.set_scale:
                    scale = task[1]
                    self.set_scale(scale)
                elif task[0] == _UIEvents.set_image:
                    image = task[1]
                    self.set_image(image)
                elif task[0] == _UIEvents.set_resolution:
                    resolution = task[1]
                    self.set_resolution(resolution)
                elif task[0] == _UIEvents.reset_image:
                    resolution = task[1]
                    self.reset_image(resolution)
                elif task[0] == _UIEvents.set_column:
                    column, column_num = task[1]
                    self.set_column(column, column_num)
                elif task[0] == _UIEvents.plot:
                    t_values, dist_values = task[1]
                    self.plot(t_values, dist_values)
            
            # Update the display
            time.sleep(0.1)
            self.update_display()
    
    # Showing images
    def update_display(self):
        if self.display_initialized:

            surface = pygame.surfarray.make_surface(self.upscaled_image())
            self.display.blit(surface, (0, 0))
            pygame.display.flip()
        
    def set_image(self, image: np.ndarray):
        self.set_resolution(image.shape[:2])
        self.image = image

        self.logger.debug(f"Image set to shape {image.shape}.")

        self.update_display()

    def set_resolution(self, resolution: Tuple[int, int]):
        self.resolution = int(resolution[0]), int(resolution[1])
        self.display = pygame.display.set_mode(resolution)
        self.display_initialized = True
        self.logger.debug(f"Resolution set to {resolution}.")

    def reset_image(self, resolution: Tuple[int, int]):
        self.image = np.zeros(resolution + (3,), dtype=np.uint8)
        self.set_resolution(resolution)

    def set_column(self, column: np.ndarray, column_num = int): # line_number je št stolpca
        if self.image is None:
            self.logger.debug(f"Image not set.")
            raise ValueError("Image not set.")
            return
        if column.shape != (self.image.shape[1], self.image.shape[2]):
            self.logger.debug(f"Column shape does not match image shape.")
            raise ValueError("Column shape does not match image shape.")
        if column_num >= self.image.shape[0]:
            self.logger.debug(f"Column number out of bounds.")
            raise ValueError("Column number out of bounds.")
        
        # self.logger.debug(f"Setting column {column_num}, to max val {np.max(column)}.")
        self.image[column_num] = column

        self.update_display()

    # Plotting
    def plot(self, t_values: np.ndarray, dist_values: np.ndarray):
        plt.plot(t_values, dist_values, label=f"eq(t)")
        plt.xlabel('t')
        plt.ylabel('o(t)')
        plt.grid(True)
        plt.show(block=True)
        exit(0)

    # Upscaling
    def set_scale(self, scale: int):
        self.scale = int(scale)

    def upscaled_image(self):
        if self.scale == 1:
            return self.image
        if self.resolution[0] != self.image.shape[0] * self.scale:
            self.set_resolution((self.image.shape[0] * self.scale, self.image.shape[1] * self.scale))
        return np.repeat(np.repeat(self.image, self.scale, axis=0), self.scale, axis=1)

    # Other
    def stop(self):
        self.logger.info("Stopping UI thread.")
        pygame.quit()