"""
BARE BONES VERSION (ALPHA, NEEDS FEATURES TO MAKE IT MORE USEABLE)
- CAN ONLY MOVE CURSOR
"""

import asyncio
import cv2
import mediapipe as mp
import pyautogui

# Set pyautogui settings
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
AVERAGING_TIMES = 30 # recommended 30
average_pos = []

for i in range(AVERAGING_TIMES):
    average_pos.append((0,0))
    
    
async def main():
    
    # Initiate cv2
    cap = cv2.VideoCapture()
    print("Loading CV2...")
    cap.open(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 60)
    print("Done!")

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # media pipe utlities
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(max_num_faces=1)
    drawing_utils = mp.solutions.drawing_utils

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)      
        face = output.multi_face_landmarks
        
        if face:
            
            top_left = (0,0)
            top_right = (0,0)
            bottom_left = (0,0)
            bottom_right = (0,0)
            center = (0,0)
            bottom_center = (0,0)
            
            for points in face:
                # drawing_utils.draw_landmarks(frame, points)
                landmarks = points.landmark
                
                for id, landmark in enumerate(landmarks):
                    x = int(landmark.x * frame_width)
                    y = int(landmark.y * frame_height)
                    
                    if id == 33:
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 255, 0)) # green pointer
                        top_left = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    if id == 263:
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 255, 0)) # green pointer
                        top_right = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    if id == 61:
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 255, 0)) # green pointer
                        bottom_left = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    if id == 291:
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 255, 0)) # green pointer
                        bottom_right = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    if id == 1:
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 255, 0)) # green pointer
                        center = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                        
                    if id == 199:
                        cv2.circle(frame, center=(x, y), radius=10, color=(0, 255, 0)) # green pointer
                        bottom_center = [SCREEN_WIDTH / frame_width * x, SCREEN_HEIGHT / frame_height * y]
                
            
            # x position logic
            delta_center_bottom_left = center[0] - bottom_left[0]
            delta_center_bottom_right = bottom_right[0] - center[0]
            
            # print(delta_center_bottom_left, delta_center_bottom_right, delta_center_bottom_left-delta_center_bottom_right)
            
            # y position logic
            delta_center_top_left = center[1] - top_left[1]
            delta_center_top_right = center[1] - top_right[1]
            average_top_center = (delta_center_top_left+delta_center_top_right)/2
            print(average_top_center)
            
            # movement
            cursor_pos = (delta_center_bottom_left-delta_center_bottom_right+68)*15, (average_top_center-57)*50
            average_pos.append(cursor_pos)
            average_pos.pop(0)
            
            # print(average_pos)

            average_x = 0
            average_y = 0
            for i in range(-1, -AVERAGING_TIMES-1, -1):
                average_x += average_pos[i][0]
                average_y += average_pos[i][1]
            average_x /= AVERAGING_TIMES
            average_y /= AVERAGING_TIMES
            
            # print(average_x, average_y)  
                          
            pyautogui.moveTo(average_x, average_y)

        # final output!!!
        cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        cv2.imshow("test", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
       
            
    cap.release()
    cv2.destroyAllWindows()

asyncio.run(main())