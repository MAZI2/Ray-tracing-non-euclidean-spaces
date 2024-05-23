import pygame
import queue
import numpy as np
import time

import logging
logger = logging.getLogger(__name__)

class _UIEvents:
    quit = "quit"
    set_image = "set_image"

_ui_command_queue = queue.Queue()

class UI:
    """Events that can be sent to the UI thread."""

    # Send events

    @staticmethod
    def set_image(image: np.ndarray):
        _ui_command_queue.put((_UIEvents.set_image, (image)))

    @staticmethod
    def stop_thread():
        _ui_command_queue.put(_UIEvents.quit)


class _UIThread():
    """MUST BE RUN ON MAIN THREAD
    This class is responsible for the UI thread. It is used to display the rendered image."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Raytracer")
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
            
            # Update the display
            time.sleep(0.1)
            self.update_display()
    
    # Other func

    def update_display(self):
        if self.display_initialized:
            pygame.display.flip()
        
    def set_image(self, image: np.ndarray):
        self.display = pygame.display.set_mode(image.shape[:2])
        surface = pygame.surfarray.make_surface(image)
        self.display.blit(surface, (0, 0))
        pygame.display.flip()
        self.display_initialized = True

    def stop(self):
        pygame.quit()