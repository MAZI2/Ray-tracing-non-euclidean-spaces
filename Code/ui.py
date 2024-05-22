import pygame
import queue
import threading
import numpy as np

import typehints as th

class UI_fuck:
    """Events that can be sent to the UI thread."""
    def __init__(self):
        self._start_thread()

    def __del__(self): 
        self.stop_thread() # If the object is deleted, stop the thread
    
    # Send events

    def update_screen(self):
        self.ui_command_queue.put(th.UIEvent.update_screen)
        self.ui_task_event.set()

    def update_image(self, image: np.ndarray, resolution: th.resolution):
        self.ui_command_queue.put((th.UIEvent.update_image, (image, resolution)))
        self.ui_task_event.set()

    def stop_thread(self):
        self.ui_command_queue.put("quit")
        self.ui_task_event.set()
        self.ui_thread.join()

    # Helper functions

    def _start_thread(self):
        self.ui_command_queue = queue.Queue()
        self.ui_task_event = threading.Event()
        self.ui = UI_thread(self.ui_command_queue, self.ui_task_event)
        self.ui_thread = threading.Thread(target=self.ui.run)
        self.ui_thread.start()




class UI(threading.Thread):
    def __init__(self, command_queue: queue.Queue, task_event: threading.Event) -> None:
        self.command_queue = command_queue
        self.task_event = task_event

        pygame.init()
        pygame.display.set_caption("Raytracer")
        self.screen = None
        self.image_array = None
    
    def run(self):
        while True:
            # Handle UI
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.command_queue.put("quit")
                    self.task_event.set()
                    return
            
            # Execute tasks
            self.task_event.wait()

            # Clear
            self.task_event.clear()
            
            # Execute the commands
            while not self.command_queue.empty():
                try:
                    task = self.command_queue.get_nowait()
                    if task == th.UIEvent.quit:
                        return
                    elif task == th.UIEvent.update_screen:
                        self.update_screen()
                    elif task == th.UIEvent.update_image:
                        # Extract the image and resolution from the queue
                        self.image_array, resolution = self.command_queue.get()
                        self.set_screen(resolution)
                        self.update_image()
                except queue.Empty:
                    pass
            
            # Update the screen
            self.update_screen()

    def update_image(self):
        """Shows the rendered image."""
        if self.image_array is not None and self.screen is not None:
            surface = pygame.surfarray.make_surface(self.image_array)
            self.screen.blit(surface, (0, 0))
        self.update_screen()
    
    def update_screen(self):
        """refreshes the screen."""
        if self.screen is not None:
            pygame.display.flip()
        
    def set_screen(self, resolution):
        """Sets the screen to the specified resolution."""
        self.screen = pygame.display.set_mode(resolution)




