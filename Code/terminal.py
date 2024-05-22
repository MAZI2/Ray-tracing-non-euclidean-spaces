import threading
import queue


class Terminal:
    def __init__(self):
        self._start_thread()
    
    # Helper functions

    def _start_thread(self):
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()
        self.task_event = threading.Event()
        self.thread = Terminal_thread(self.in_queue, self.out_queue, self.task_event)
        self.thread.start()
        

class Terminal_thread(threading.Thread):
    def __init__(self, in_queue: queue.Queue, out_queue: queue.Queue, task_event: threading.Event) -> None:
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.task_event = task_event

    def run(self):
        while True:
            # Execute tasks
            self.task_event.wait()

            # Clear
            self.task_event.clear()
            
            # Execute the commands
            while not self.in_queue.empty():
                try:
                    task = self.in_queue.get_nowait()
                    if task == "quit":
                        return
                    elif task == "print":
                        # Print what is in the in_queue

                except queue.Empty:
                    pass

