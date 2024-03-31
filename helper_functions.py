import pyautogui
import math

def midpoint(point_x, point_y, point_2x, point_2y):
    return int((point_x+point_2x)//2),int((point_y+point_2y)//2)

def set_opencv(cap, cv2, screen_width, screen_height):
    print(f"screen width, height: {screen_width}, {screen_height}")
    print("Loading CV2...")
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    cap.open(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 60)
    print("Done!")
    return cap

def click_mechanics(distance, click_distance, click_status, handType):
    
    if distance < click_distance and click_status == 0 and handType != None:
        click_status = 1
        pyautogui.mouseDown()
        # print(F"click dist: {distance}")
        return click_status

    elif distance > 100 and handType != None:
        click_status = 0
        pyautogui.mouseUp()
        return click_status
    
    else:
        click_status = 1
        return click_status
    
def ptp_distance(point1: tuple, point2: tuple):
    # Pythagorean theorem to calculate distance between thumb and index
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)