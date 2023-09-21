'''
NOTE: RECOMMENDED THAT WEBCAM AND MONITOR IS 1920x1080 or a multiple or 2 or 1.5.
UPDATE NOTE: ADDED ONE FRAME BUFFER TO INCREASE SMOOTHENING
'''
import cv2
import mediapipe as mp
import pyautogui
import asyncio
import math
import time

# global constants 
screen_width = 1920
screen_height = 1080

async def main():
    # grabs screen resolution
    # screen_width, screen_height = pyautogui.size()
    print(f"screen width, height: {screen_width}, {screen_height}")

    print("Loading CV2...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("Done!")

    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = False

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
                        cv2.circle(frame, center=(x, y), radius=30, color=(0, 255, 0)) # green pointer
                        
                        index_x = screen_width / frame_width * x
                        index_y = screen_height / frame_height * y

                    if id == 4: 
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 0, 255)) # smaller red pointer
                        
                        thumb_x = screen_width / frame_width * x
                        thumb_y = screen_height / frame_height * y
                        
                        # cursor moving algorithm 
                        if abs(index_y - thumb_y) > 100:
                            old_cursor_x_1 = previous_mouse_pos_1[0]
                            old_cursor_y_1 = previous_mouse_pos_1[1]

                            calc_cursor_x = (index_x+old_cursor_x_1)/2
                            calc_cursor_y = (index_y+old_cursor_y_1)/2
                            pyautogui.moveTo(calc_cursor_x, calc_cursor_y)

                            previous_mouse_pos_1 = [calc_cursor_x,calc_cursor_y]
                        
                        # Pythagorean theorem to calculate distance between thumb and index
                        index_thumb_distance = math.sqrt(abs(index_y-thumb_y)**2+abs(index_x-thumb_x)**2)
                        
                        try:
                            if index_thumb_distance < 60 and index_thumb_distance > 14: # optimized using histogram pattern
                                pyautogui.mouseDown()
                                status_message = "left click!"
                                print(F"click dist: {index_thumb_distance}")
                            else:
                                pyautogui.mouseUp()
                        except:
                            print('error: attempted to click')
                            
            # draws line between index and thumb, adds distance on midpoint of line
            cv2.line(frame, (int(index_x), int(index_y)), (int(thumb_x), int(thumb_y)), (255, 0, 0), 3)
            line_midpoint_x = (index_x+thumb_x) // 2
            line_midpoint_y = (index_y+thumb_y) // 2
            cv2.putText(frame, f"Distance: {round(index_thumb_distance)}", (int(line_midpoint_x), int(line_midpoint_y)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
    
        new_frame_time = time.time()
        
        # FPS calculator
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        
        # Status indicators in THIS ORDER: FPS, Index cord, thumb cord, click stat
        cv2.putText(frame, f"Index finger: {index_x}, {index_y}", (int(50), int(50)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Thumb finger: {thumb_x}, {thumb_y}", (int(50), int(90)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Click status: {status_message}", (int(50), int(130)), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"fps: {int(fps)}", (50, 180), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,0), 2, cv2.LINE_AA)
        
        # final output!!!
        cv2.namedWindow("Virtual Mouse", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Virtual Mouse", 1920//2, 1080//2)
        cv2.imshow('Virtual Mouse', frame)
        frame_number += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())
