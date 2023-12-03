'''
NOTE: RECOMMENDED THAT WEBCAM IS 1920x1080. MANUALLY SET SCREEN RES!

UPDATE NOTES:
September 2023: ADDED AVERAGING BUFFER TO INCREASE SMOOTHENING AND INCREASE HAND PRECISION
DECEMBER 2023: ADDED RELATIVE DISTANCE CLICKING TO COMPENSTE FOR PIXEL DISTANCE CLICKING BY ADDING A RELATIVE LINE (UPPER TO LOWER PALM)
DECEMBER 2023: ADDED SPECTRUM CYCLING STATS!!!
'''
import cv2
import mediapipe as mp
import pyautogui
import asyncio
import math
import time
import numpy as np

# global constants
# screen_width, screen_height = pyautogui.size()
global_scale = 1
window_start_scale = 2
screen_width = 1920
screen_height = 1080
show_window = True
click_mechanic_aceleration_threshold = 1.6
WINDOW_NAME = "Virtual Mouse: q(exit), w(hide/show stats), e(zero dist. dragging), r(RGB 4on/off)"
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False
click_distance = 120

# global variables
click_status = 0
zero_distance_dragging = False
show_stats = True
rgb_stat = True

def generate_spectrum_color(color, speed):
    # Convert color to HSV
    hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]

    # Update hue based on speed
    hsv[0] = (hsv[0] + speed) % 180

    # Convert back to BGR
    new_color = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2BGR)[0][0]

    return tuple(map(int, new_color))

def midpoint(point_x, point_y, point_2x, point_2y):
    return int((point_x+point_2x)//2),int((point_y+point_2y)//2)

def click_mechanics(distance):
    global click_status
    
    if distance < click_distance and click_status == 0:
        click_status = 1
        pyautogui.mouseDown()
        # print(F"click dist: {distance}")
        return

    elif distance > 100:
        click_status = 0
        pyautogui.mouseUp()
    
def ptp_distance(point1: tuple, point2: tuple):
    # Pythagorean theorem to calculate distance between thumb and index
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

async def main():
    global click_status
    global show_stats
    global zero_distance_dragging
    global rgb_stat
    
    print(f"screen width, height: {screen_width}, {screen_height}")

    print("Loading CV2...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(1920/global_scale))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(1080/global_scale))
    print("Done!")

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # media pipe utlities
    mp_hands = mp.solutions.hands.Hands(max_num_hands = 1)
    
    drawing_utils = mp.solutions.drawing_utils

    color = (120, 255, 255)
    
    frame_number = 0

    index_y = 0
    index_x = 0

    thumb_x = 0
    thumb_y = 0

    prev_frame_time = 0
    new_frame_time = 0

    previous_mouse_pos_1 = [0,0]
    previous_mouse_pos_2 = [0,0]
    
    previous_lower_palm_pos2 = (0,0)
    previous_lower_palm_pos1 = (0,0)

    relative_lower_palm_aceleration_display = 0
    
    while True:
        new_frame_time = time.time()
        
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = mp_hands.process(rgb_frame)
        hands = output.multi_hand_landmarks

        if hands:
            
            for hand in hands:
                drawing_utils.draw_landmarks(frame, hand)
                landmarks = hand.landmark
                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    
                    # UPPER LOWER PALM
                    if id == 17:
                        cv2.circle(frame, center=(x, y), radius=30//global_scale, color=(255, 0, 0)) # blue pointer
                        
                        upper_palm_x = screen_width / frame_width * x
                        upper_palm_y = screen_height / frame_height * y
                        
                    if id == 0:
                        cv2.circle(frame, center=(x, y), radius=30//global_scale, color=(255, 0, 0)) # blue pointer
                        
                        lower_palm_x = screen_width / frame_width * x
                        lower_palm_y = screen_height / frame_height * y
                        
                        # CAPTURE A SAMPLE EVERY 2 FRAMES
                        if frame_number % 2 == 0:
                            previous_lower_palm_pos2 = (lower_palm_x, lower_palm_y)
                            
                        else:
                            previous_lower_palm_pos1 = (lower_palm_x, lower_palm_y)
                        
                    # INDEX THUMB
                    if id == 8:
                        cv2.circle(frame, center=(x, y), radius=30//global_scale, color=(0, 255, 0)) # green pointer
                        
                        index_x = screen_width / frame_width * x
                        index_y = screen_height / frame_height * y
            
                    if id == 4: 
                        cv2.circle(frame, center=(x, y), radius=10//global_scale, color=(255, 0, 0)) # smaller red pointer
                        
                        thumb_x = screen_width / frame_width * x
                        thumb_y = screen_height / frame_height * y
                        
                        # Distance from index to thumb (pythagorean)
                        index_thumb_distance = ptp_distance((thumb_x,thumb_y), (index_x, index_y))
                        
                        # cursor moving algorithm and threshold setter
                        if zero_distance_dragging == True:
                            dragging_threshold = 0
                        else:
                            dragging_threshold = 100
            
            palm_distance_reciprocal = 1/ptp_distance((lower_palm_x,lower_palm_y),(upper_palm_x,upper_palm_y))
            relative_palm_index_thumb_distance = index_thumb_distance*palm_distance_reciprocal*300
                                
            if show_window and global_scale == 1:
                # draws line between index and thumb, adds distance on midpoint of line
                cv2.line(frame, (int(index_x), int(index_y)), (int(thumb_x), int(thumb_y)), (255, 0, 0), 3)
                thumb_index_line_midpoint = midpoint(index_x,index_y,thumb_x,thumb_y)
                cv2.putText(frame, f"Relative ThumbIndex: {round((relative_palm_index_thumb_distance),3)}", thumb_index_line_midpoint, cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
                
                # draws line between upper and lower palm
                cv2.line(frame, (int(lower_palm_x), int(lower_palm_y)), (int(upper_palm_x), int(upper_palm_y)), (255, 0, 0), 3)
                palm_line_midpoint = midpoint(lower_palm_x,lower_palm_y,upper_palm_x,upper_palm_y)
                cv2.putText(frame, f"Palm Distance Recip.: {round((palm_distance_reciprocal),4)}", palm_line_midpoint, cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)

            # Aceleration metrics
            average_lower_palm_pos = ((previous_lower_palm_pos2[0] + previous_lower_palm_pos1[0])/2, (previous_lower_palm_pos2[1] + previous_lower_palm_pos1[1])/2)
            relative_lower_palm_aceleration = ptp_distance(average_lower_palm_pos, (lower_palm_x,lower_palm_y)) * palm_distance_reciprocal * 40
            
            # TRIGGER MOVING MECHANICS AND AVERAGING MECH IF ACELERATION AND DRAGGING THRESHOLD MET
            if relative_palm_index_thumb_distance > dragging_threshold and relative_lower_palm_aceleration > 0.4:
                old_cursor_x_1 = previous_mouse_pos_1[0]
                old_cursor_y_1 = previous_mouse_pos_1[1]
                
                old_cursor_x_2 = previous_mouse_pos_2[0]
                old_cursor_y_2 = previous_mouse_pos_2[1]

                calc_cursor_x = (index_x+old_cursor_x_1+old_cursor_x_2)/3
                calc_cursor_y = (index_y+old_cursor_y_1+old_cursor_y_2)/3
                pyautogui.moveTo(calc_cursor_x, calc_cursor_y)

                if frame_number % 2 == 0:
                    previous_mouse_pos_2 = [calc_cursor_x,calc_cursor_y]
                else:
                    previous_mouse_pos_1 = [calc_cursor_x,calc_cursor_y]
            
            # Trigger clicking mechanic if aceleration metrics are met
            if relative_lower_palm_aceleration < click_mechanic_aceleration_threshold:
                click_mechanics(relative_palm_index_thumb_distance)
                
            if frame_number % 2:
                relative_lower_palm_aceleration_display = relative_lower_palm_aceleration
        
            with open("metrics1.txt", "a") as metricsdoc1:
                metricsdoc1.write(str(index_thumb_distance) + "\n")
                
            with open("metrics2.txt", "a") as metricsdoc2:
                metricsdoc2.write(str(relative_palm_index_thumb_distance) + "\n")
                

        elif click_status == 1:
            # Stop clicking when hands aren't in frame
            click_mechanics(click_distance+1)
        
        new_frame_time = time.time()
        
        # FPS calculator
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        
        if show_window:
            
            if global_scale == 1:
                text_size = 2
            else:
                text_size = 1
            
            if show_stats == True:
                
                if rgb_stat == True:
                    # Spectrum cycles text :)
                    color = generate_spectrum_color(color, 3)
                
                # Status indicators in THIS ORDER: FPS, Index cord, thumb cord, click stat, hand relative distance from camera
                cv2.putText(frame, f"Index finger: {index_x}, {index_y}", (int(50/global_scale), int(50/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, color, text_size, cv2.LINE_AA)
                cv2.putText(frame, f"Thumb finger: {thumb_x}, {thumb_y}", (int(50/global_scale), int(90/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, color, text_size, cv2.LINE_AA)
                cv2.putText(frame, f"Click status: {click_status}", (int(50/global_scale), int(130/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, color, text_size, cv2.LINE_AA)
                cv2.putText(frame, f"fps: {int(fps)}", (int(50//global_scale), int(180/global_scale)), cv2.FONT_HERSHEY_PLAIN, 3/global_scale, color, text_size, cv2.LINE_AA)
                cv2.putText(frame, f"Aceleration (relative unit/2s): {round((relative_lower_palm_aceleration_display),2)}", (int(50//global_scale), int(230/global_scale)),cv2.FONT_HERSHEY_PLAIN, 3/global_scale, color, text_size, cv2.LINE_AA)
                cv2.putText(frame, f"Zero dist. dragging: {zero_distance_dragging}", (int(50//global_scale), int(280/global_scale)),cv2.FONT_HERSHEY_PLAIN, 3/global_scale, color, text_size, cv2.LINE_AA)
                cv2.putText(frame, f"RGB: {rgb_stat}", (int(50//global_scale), int(330/global_scale)),cv2.FONT_HERSHEY_PLAIN, 3/global_scale, color, text_size, cv2.LINE_AA)

            # final output!!!
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

            if frame_number == 0:
                cv2.resizeWindow(WINDOW_NAME, int(screen_width/window_start_scale), int(screen_height/window_start_scale))
                print('Scaled CV2 Window Size!')

            cv2.imshow(WINDOW_NAME, frame)

        frame_number += 1
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        
        if key == ord('w'):
            show_stats = not show_stats
        
        if key == ord('e'):
            zero_distance_dragging = not zero_distance_dragging
        
        if key == ord('r'):
            rgb_stat = not rgb_stat
            
        elif cv2.getWindowProperty(WINDOW_NAME,cv2.WND_PROP_VISIBLE) < 1:        
            break    
            
    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())
