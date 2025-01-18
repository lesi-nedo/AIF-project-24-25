import threading
import queue
from typing import Optional, List
import matplotlib
from IPython import display
import matplotlib.pyplot as plt
import numpy as np
import logging

logger = logging.getLogger(__name__)


# Add DisplayThread class after imports
class DisplayThread(threading.Thread):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height
        self.queue = queue.Queue(maxsize=2)
        self.log_queue = queue.Queue(maxsize=5)
        self.running = True
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.img_plot = None
        self.frame_counter = 0
        self.skip_frames = 8

    def get_latest_logs(self) -> List[str]:
        logs = []
        # Create a temporary list of all logs
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        # Put them back in the queue
        for log in logs:
            self.log_queue.put(log)
        return logs

    def add_log(self, message: str) -> None:
        """Thread-safe method to add a log message"""
        try:
            if self.log_queue.full():
                # Remove oldest log if queue is full
                try:
                    self.log_queue.get_nowait()
                except queue.Empty:
                    pass
            self.log_queue.put_nowait(message)
        except queue.Full:
            pass  # Skip if queue is full
        
    def run(self):
        self._init_display()
        while self.running:
            
            try:
                # Skip frames
                self.frame_counter += 1
                if self.frame_counter % self.skip_frames != 0:
                    continue

                # Non-blocking queue get with timeout
                screen_data = self.queue.get(timeout=0.001)
                self._update_display(screen_data)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Display thread error: {e}")
                
    def _init_display(self):
    #     matplotlib.use('module://ipykernel.pylab.backend_inline')
    #     plt.ioff()
        
    #    # Create figure and display area for messages
    #     self.fig = plt.figure(figsize=(10, 12), dpi=80)
        
    #     # Main game display
    #     self.ax = self.fig.add_subplot(2, 1, 1)  # Top subplot for game
    #     self.ax.set_xlim(0, self.width)
    #     self.ax.set_ylim(0, self.height)
    #     self.ax.axis("off")
    #     self.ax.set_aspect("equal")
    #     self.ax.set_title("Game Scene")
    #     # Initialize image plot with optimized settings
    #     self.img_plot = self.ax.imshow(
    #         np.zeros((self.height, self.width, 3), dtype=np.uint8),
    #         interpolation='nearest',  # Faster interpolation
    #         animated=True  # Optimize for animation
    #     )
    #     # Text area for messages
    #     self.text_ax = self.fig.add_subplot(2, 1, 2)  # Bottom subplot for text
    #     self.text_ax.axis('off')
    #     self.text_box = self.text_ax.text(0.05, 0.95, '', 
    #                                     transform=self.text_ax.transAxes,
    #                                     verticalalignment='top',
    #                                     fontfamily='monospace')
        
        
    #     self.fig.tight_layout()
        
    #     plt.close('all')
    #     display.clear_output(wait=True)
    #     self.display_handle = display.display(self.fig, display_id=True)
        pass
        
    def _update_display(self, screen_data):
        if not isinstance(screen_data, bytes):
            return
            
        try:
            nparr = np.frombuffer(screen_data, np.uint8)
            img = nparr.reshape((self.height, self.width, 3))
            img = np.flipud(img)
            
            self.img_plot.set_array(img)
            
            # Update text less frequently
            if self.frame_counter % 14 == 0:  # Update text every 14th frame
                latest_logs = '\n'.join(self.get_latest_logs())
                self.text_box.set_text(latest_logs)

            # Minimal redraw
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
            
            # Update display
            self.display_handle.update(self.fig)
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
            
    def stop(self):
        self.running = False
        if self.fig:
            plt.close(self.fig)
