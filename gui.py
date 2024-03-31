import numpy as np
import cv2
import time

class FPS():
    def __init__(self, start_time):
        self.start_time = start_time
        
        self.fps = 0
        self.fps_average = 0
        self.frame_number = 0
        
        self.prev_frame_time = 0
        self.new_frame_time = 0
        
    def new_frame(self, add_frame_count = False):
        
        if add_frame_count:
            self.frame_number += 1
        
        self.new_frame_time = time.time()
        return self.frame_number
        
    def calc_fps(self):
        self.fps = 1/(self.new_frame_time-self.prev_frame_time)
        self.fps_average = self.frame_number/(time.time()-self.start_time)
        self.prev_frame_time = self.new_frame_time

        return self.fps, self.fps_average
    
    def get_frame_number(self):
        return self.frame_number
        
def generate_spectrum_color(color, speed):
    # Convert color to HSV
    hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]

    # Update hue based on speed
    hsv[0] = (hsv[0] + speed) % 180

    # Convert back to BGR
    new_color = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0]

    return tuple(map(int, new_color))

def show_stats(frame, index_x, index_y, global_scale, thumb_x, thumb_y, color, text_size, click_status, fps, fps_average, zero_distance_dragging, relative_lower_palm_aceleration, rgb_stat, handType):
    
    display_list = [
    f"Index finger: {index_x}, {index_y}",
    f"Thumb finger: {thumb_x}, {thumb_y}",
    f"Click status: {click_status}",
    f"FPS (live, average): {round(fps)}, {round((fps_average),2)}",
    f"Aceleration (relative unit/2s): {round((relative_lower_palm_aceleration),2)}",
    f"Zero dist. dragging: {zero_distance_dragging}",
    f"RGB: {rgb_stat}",
    f"Hand: {handType}"
    ]
    
    for text_index in range(len(display_list)):
        cv2.putText(frame, display_list[text_index], (int(50/global_scale), int(text_index*50+50/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, color, text_size, cv2.LINE_AA)