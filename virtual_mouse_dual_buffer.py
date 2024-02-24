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
import time

import gui
import helper_functions

GLOBAL_SCALE = 1
WINDOW_START_SCALE = 2
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SHOW_WINDOW = False
CLICK_ACELERATION_THRESHOLD = 35 # 50-100 are good for a camera w/ mildish motion blur. 15-50 for a good webcam 
CLICK_DISTANCE = 120
WINDOW_NAME = "Virtual Mouse: q(exit), w(hide/show stats), e(zero dist. dragging), r(RGB 4on/off)"

# Set pyautogui settings
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

async def main():
    
    # Initiate cv2
    cap = cv2.VideoCapture()
    helper_functions.set_opencv(cap, cv2, SCREEN_WIDTH, SCREEN_HEIGHT)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # media pipe utlities
    mp_hands = mp.solutions.hands.Hands(model_complexity = 0, 
                                        max_num_hands=1,
                                        min_detection_confidence=0.5,
                                        min_tracking_confidence=0.5)
    drawing_utils = mp.solutions.drawing_utils

    # Class instances
    fps_instance = gui.FPS(start_time = time.time())
    
    # Operation variables
    zero_distance_dragging = False
    show_stats = True
    rgb_stat = True
    click_status = 0
    color = (120, 255, 255)
    index = [0, 0]
    thumb = [0, 0]
    previous_mouse_pos_1 = [0,0]
    previous_mouse_pos_2 = [0,0]
    previous_lower_palm_pos = (0,0)
    relative_lower_palm_aceleration = 0
    
    while True:
        fps_instance.new_frame()
        
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = mp_hands.process(rgb_frame)      
        hands = output.multi_hand_landmarks
        handType = None
        
        if hands:
            
            # Hand type
            for hand in output.multi_handedness:
                handType = hand.classification[0].label
            
            for hand in hands:
                drawing_utils.draw_landmarks(frame, hand)
                landmarks = hand.landmark
                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    
                    # UPPER PALM
                    if id == 17:
                        cv2.circle(frame, center=(x, y), radius=30//GLOBAL_SCALE, color=(0, 255, 0)) # blue pointer
                        upper_palm = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                    
                    # Pinky finger
                    if id == 20:
                        pinky = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    # LOWER PALM
                    if id == 0:
                        cv2.circle(frame, center=(x, y), radius=30//GLOBAL_SCALE, color=(255, 0, 0)) # blue pointer
                        lower_palm = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    # INDEX
                    if id == 8:
                        cv2.circle(frame, center=(x, y), radius=30//GLOBAL_SCALE, color=(255, 0, 0)) # green pointer
                        index = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]

                    # THUMB
                    if id == 4: 
                        cv2.circle(frame, center=(x, y), radius=10//GLOBAL_SCALE, color=(255, 0, 0)) # smaller red pointer
                        
                        thumb = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                        index_thumb_distance = helper_functions.ptp_distance((thumb[0],thumb[1]), (index[0], index[1]))
            
            palm_distance_reciprocal = 1/helper_functions.ptp_distance((lower_palm[0],lower_palm[1]),(upper_palm[0],upper_palm[1]))
            relative_palm_index_thumb_distance = index_thumb_distance*palm_distance_reciprocal*300
                                
            if SHOW_WINDOW and GLOBAL_SCALE == 1:
                # draws line between index and thumb, adds distance on midpoint of line
                cv2.line(frame, (int(index[0]), int(index[1])), (int(thumb[0]), int(thumb[1])), (255, 0, 0), 3)
                thumb_index_line_midpoint = helper_functions.midpoint(index[0],index[1],thumb[0],thumb[1])
                cv2.putText(frame, f"Relative ThumbIndex: {round((relative_palm_index_thumb_distance),3)}", thumb_index_line_midpoint, cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
                
                # draws line between upper and lower palm
                cv2.line(frame, (int(lower_palm[0]), int(lower_palm[1])), (int(upper_palm[0]), int(upper_palm[1])), (255, 0, 0), 3)
                palm_line_midpoint = helper_functions.midpoint(lower_palm[0],lower_palm[1],upper_palm[0],upper_palm[1])
                cv2.putText(frame, f"Palm Distance Recip.: {round((palm_distance_reciprocal),4)}", palm_line_midpoint, cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)

            # Aceleration metrics
            relative_lower_palm_aceleration = helper_functions.ptp_distance(previous_lower_palm_pos, (lower_palm[0],lower_palm[1])) * palm_distance_reciprocal * 300
            
            # set new previous lower palm position
            previous_lower_palm_pos = (lower_palm[0], lower_palm[1])

            # TRIGGER MOVING MECHANICS AND AVERAGING MECH IF ACELERATION AND DRAGGING THRESHOLD MET
            if zero_distance_dragging == True:
                dragging_threshold = 0
            else:
                dragging_threshold = 100
            
            if relative_palm_index_thumb_distance > dragging_threshold and relative_lower_palm_aceleration > 5.2:

                calc_cursor_x = (upper_palm[0]+previous_mouse_pos_1[0]+previous_mouse_pos_2[0])/3
                calc_cursor_y = (upper_palm[1]+previous_mouse_pos_1[1]+previous_mouse_pos_2[1])/3
                
                pyautogui.moveTo(calc_cursor_x, calc_cursor_y)
                
                # Set previous mouse positions (1 and 2) for every even and odd frame
                if fps_instance.get_frame_number() % 2 == 0:
                    previous_mouse_pos_2 = [calc_cursor_x,calc_cursor_y]
                else:
                    previous_mouse_pos_1 = [calc_cursor_x,calc_cursor_y]
            
            # Trigger clicking mechanic if aceleration metrics are met
            if relative_lower_palm_aceleration < CLICK_ACELERATION_THRESHOLD:
                click_status = helper_functions.click_mechanics(relative_palm_index_thumb_distance, CLICK_DISTANCE, click_status)
                
        elif click_status == 1:
            # Stop clicking when hands aren't in frame
            click_status = helper_functions.click_mechanics(CLICK_DISTANCE+1, CLICK_DISTANCE, click_status)
        
        if SHOW_WINDOW:
            
            if GLOBAL_SCALE == 1:
                text_size = 2
            else:
                text_size = 1
            
            if show_stats == True:
                
                if rgb_stat == True:
                    # Spectrum cycles text :)
                    color = gui.generate_spectrum_color(color, 3)
                
                # Status indicators in THIS ORDER: FPS, Index cord, thumb cord, click stat, hand relative distance from camera
                fps, fps_average = fps_instance.calc_fps()
                gui.show_stats(frame, index[0], index[1], GLOBAL_SCALE, thumb[0], thumb[1], color, text_size, click_status, fps, fps_average, zero_distance_dragging, relative_lower_palm_aceleration, rgb_stat, handType)

            # final output!!!
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

            if fps_instance.get_frame_number() == 0:
                cv2.resizeWindow(WINDOW_NAME, int(SCREEN_WIDTH/WINDOW_START_SCALE), int(SCREEN_HEIGHT/WINDOW_START_SCALE))
                print('Scaled CV2 Window Size!')

            cv2.imshow(WINDOW_NAME, frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        
        if key == ord('w'):
            show_stats = not show_stats
        
        if key == ord('e'):
            zero_distance_dragging = not zero_distance_dragging
        
        if key == ord('r'):
            rgb_stat = not rgb_stat
        
        fps_instance.new_frame(add_frame_count = True)
            
    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())
