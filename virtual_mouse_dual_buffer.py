'''
NOTE: RECOMMENDED THAT WEBCAM IS 1920x1080. MANUALLY SET SCREEN RES!
UPDATE NOTE: ADDED AVERAGING BUFFER TO INCREASE SMOOTHENING AND INCREASE HAND PRECISION
'''
import cv2
import mediapipe as mp
import pyautogui
import asyncio
import math
import time

# global constants
# screen_width, screen_height = pyautogui.size()
global_scale = 4
window_start_scale = 2
screen_width = 1920
screen_height = 1080
show_window = False
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

def midpoint(point_x, point_y, point_2x, point_2y):
    return int((point_x+point_2x)//2),int((point_y+point_2y)//2)

async def main():
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
    hand_detector = mp.solutions.hands.Hands()
    drawing_utils = mp.solutions.drawing_utils

    frame_number = 0

    index_y = 0
    index_x = 0

    thumb_x = 0
    thumb_y = 0

    prev_frame_time = 0
    new_frame_time = 0

    previous_mouse_pos_1 = [0,0]
    previous_mouse_pos_2 = [0,0]


    while True:
        new_frame_time = time.time()
        
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = hand_detector.process(rgb_frame)
        hands = output.multi_hand_landmarks
        
        # mouse click status
        status_message = ""

        if hands:
            for hand in hands:
                drawing_utils.draw_landmarks(frame, hand)
                landmarks = hand.landmark
                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    
                    if id == 8:
                        cv2.circle(frame, center=(x, y), radius=30//global_scale, color=(0, 255, 0)) # green pointer
                        
                        index_x = screen_width / frame_width * x
                        index_y = screen_height / frame_height * y

                    if id == 4: 
                        cv2.circle(frame, center=(x, y), radius=10//global_scale, color=(0, 0, 255)) # smaller red pointer
                        
                        thumb_x = screen_width / frame_width * x
                        thumb_y = screen_height / frame_height * y
                        
                        # cursor moving algorithm 
                        if abs(index_y - thumb_y) > 100:
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
                            
                        
                        # Pythagorean theorem to calculate distance between thumb and index
                        index_thumb_distance = math.sqrt(abs(index_y-thumb_y)**2+abs(index_x-thumb_x)**2)
                        
                        try:
                            if index_thumb_distance < 60 and index_thumb_distance > 14:
                                pyautogui.mouseDown()
                                status_message = "left click!"
                                print(F"click dist: {index_thumb_distance}")
                            else:
                                pyautogui.mouseUp()
                        except:
                            print('error: attempted to click')

            if show_window and global_scale == 1:
                # draws line between index and thumb, adds distance on midpoint of line
                cv2.line(frame, (int(index_x), int(index_y)), (int(thumb_x), int(thumb_y)), (255, 0, 0), 3)
                line_midpoint = midpoint(index_x,index_y,thumb_x,thumb_y)
                cv2.putText(frame, f"Distance: {round(index_thumb_distance)}", line_midpoint, cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
        
        new_frame_time = time.time()
        
        # FPS calculator
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        
        if show_window:
            # Status indicators in THIS ORDER: FPS, Index cord, thumb cord, click stat
            cv2.putText(frame, f"Index finger: {index_x}, {index_y}", (int(50/global_scale), int(50/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Thumb finger: {thumb_x}, {thumb_y}", (int(50/global_scale), int(90/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Click status: {status_message}", (int(50/global_scale), int(130/global_scale)), cv2.FONT_HERSHEY_SIMPLEX, 1.3/global_scale, (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f"fps: {int(fps)}", (int(50//global_scale), int(180/global_scale)), cv2.FONT_HERSHEY_PLAIN, 3/global_scale, (0,0,255), 1, cv2.LINE_AA)
            
            # final output!!!
            cv2.namedWindow("Virtual Mouse", cv2.WINDOW_NORMAL)

            if frame_number == 0:
                cv2.resizeWindow("Virtual Mouse", int(screen_width/window_start_scale), int(screen_height/window_start_scale))
                print('Scaled CV2 Window Size!')

            cv2.imshow('Virtual Mouse', frame)

        frame_number += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())