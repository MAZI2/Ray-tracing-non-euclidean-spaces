# Imports
import queue
import numpy as np
import time
from typing import Tuple
import threading
from utilities import suppress_stdout

with suppress_stdout():
    import pygame



class _UIEvents:
    quit = "quit"
    set_image = "set_image"
    set_column = "set_column"
    set_resolution = "set_resolution"

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
    def set_column(column: np.ndarray, column_num: int):
        _ui_command_queue.put((_UIEvents.set_column, (column, column_num)))

    @staticmethod
    def stop_thread():
        _ui_command_queue.put(_UIEvents.quit)


class _UIThread(threading.Thread):
    """MUST BE RUN ON MAIN THREAD
    This class is responsible for the UI thread. It is used to display the rendered image."""
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.name = "UIThread"
        
        pygame.init()
        pygame.display.set_caption("Raytracer")
        self.image = None # (res_x, res_y, 3)
        self.display = None
        self.display_initialized = False

    def __del__(self):
        self.stop()
    
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
                elif task[0] == _UIEvents.set_image:
                    image = task[1]
                    self.set_image(image)
                elif task[0] == _UIEvents.set_resolution:
                    resolution = task[1]
                    self.set_resolution(resolution)
                elif task[0] == _UIEvents.set_column:
                    column, column_num = task[1]
                    self.set_column(column, column_num)
            
            # Update the display
            time.sleep(0.1)
            self.update_display()
    
    # Other func

    def update_display(self):
        if self.display_initialized:
            surface = pygame.surfarray.make_surface(self.image)
            self.display.blit(surface, (0, 0))
            pygame.display.flip()
        
    def set_image(self, image: np.ndarray):
        self.set_resolution(image.shape[:2])
        self.image = image

        self.update_display()

    def set_resolution(self, resolution: Tuple[int, int]):
        resolution = int(resolution[0]), int(resolution[1])
        self.display = pygame.display.set_mode(resolution)
        self.image = np.zeros(resolution + (3,), dtype=np.uint8)
        self.display_initialized = True

    def set_column(self, column: np.ndarray, column_num = int): # line_number je št stolpca
        if self.image is None:
            logger.error("Cannot set line, resolution not set.")
            return
        if column.shape != (self.image.shape[1], self.image.shape[2]):
            logger.error("Line has different length or channel number than the image.")
            return
        if column_num >= self.image.shape[0]:
            logger.error("Column number out of bounds.")
            return
        
        logger.debug(f"Setting column {column_num}, to max val {np.max(column)}.")
        self.image[column_num] = column

        self.update_display()


    def stop(self):
        pygame.quit()