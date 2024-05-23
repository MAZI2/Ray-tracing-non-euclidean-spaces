import pygame
import queue
import numpy as np

import typehints as th

_ui_command_queue = queue.Queue()

class UI:
    """Events that can be sent to the UI thread."""

    # Send events
    @staticmethod
    def update_screen():
        _ui_command_queue.put(th.UIEvent.update_screen)

    @staticmethod
    def update_image(image: np.ndarray, resolution: th.resolution):
        _ui_command_queue.put((th.UIEvent.update_image, (image, resolution)))

    @staticmethod
    def stop_thread():
        _ui_command_queue.put(th.UIEvent.quit)


class _UIThread():
    """MUST BE RUN ON MAIN THREAD
    This class is responsible for the UI thread. It is used to display the rendered image."""
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Raytracer")
        self.screen = None
        self.image_array = None

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
                if task == th.UIEvent.quit:
                    running = False
                elif task[0] == th.UIEvent.update_image:
                    self.image_array, resolution = task[1]
                    self.set_screen_resolution(resolution)
                    self.update_image()
                elif task == th.UIEvent.update_screen:
                    self.update_screen()
            
            # Update the screen
            self.update_screen()

    def update_image(self):
        """Shows the rendered image."""
        if self.image_array is not None and self.screen is not None:
            surface = pygame.surfarray.make_surface(self.image_array)
            self.screen.blit(surface, (0, 0))
            pygame.display.flip()
    
    def update_screen(self):
        pygame.display.flip()
        
    def set_screen_resolution(self, resolution):
        self.screen = pygame.display.set_mode(resolution)

    def stop(self):
        pygame.quit()