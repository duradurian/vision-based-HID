import cv2 as cv2

def aruco_display(corners, ids, image):
        if len(corners) > 0:
    
            ids = ids.flatten()
                
            for (markerCorner, markerID) in zip(corners, ids):
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
    
    
                top_color = (255,0,0)
                bottom_color = (255,0,0)
                
                topRight = (int(topRight[0]), int(topRight[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))

                slope_top = (topRight[1] - topLeft[1]) / (topRight[0] - topLeft[0])
                slope_bottom = (bottomRight[1] - bottomLeft[1]) / (bottomRight[0] - bottomLeft[0])
                
                tag_midpoint = (int((topRight[0] + topLeft[0] + bottomLeft[0] + bottomRight[0])/4), int((topRight[1] + topLeft[1] + bottomLeft[1] + bottomRight[1])/4))
                cv2.circle(image, tag_midpoint, 10, (255,255,0), 2)
                
                tag_in_aim = (tag_midpoint[0] - 1280/2)**2 + (tag_midpoint[1] - 720/2)**2 < 50**2
                
                if tag_in_aim:
                    circle_color = (0,255,0)
                else:
                    circle_color = (0,0,255)
                
                cv2.circle(image, (int(1280/2), int(720/2)), 50, circle_color, 2)
                
                
                if abs(slope_top) < 0.03:
                    top_color = (0, 255, 0)
                    
                if abs(slope_bottom) < 0.03:
                    bottom_color = (0, 255, 0)
                    
                if abs(slope_bottom) < 0.03 and abs(slope_top) < 0.03 and tag_in_aim:
                    cv2.putText(image, "READY TO SHOOT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
                    
                # PUT SLOPE NUMBERS ON MIDPOINTS OF THE LINES
                midpoint_top = (int((topRight[0]+topLeft[0])/2), int((topRight[1]+topLeft[1])/2)-10)
                midpoint_bottom = (int((bottomRight[0]+bottomLeft[0])/2), int((bottomRight[1]+bottomLeft[1])/2)-10)
                cv2.putText(image, str(round(slope_top, 3)), midpoint_top, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 1, cv2.LINE_AA)
                cv2.putText(image, str(round(slope_bottom, 3)), midpoint_bottom, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (2055,0,255), 1, cv2.LINE_AA)
                
                
                cv2.line(image, topLeft, topRight, top_color, 3)
                cv2.line(image, topRight, bottomRight, (255, 0, 0), 3)
                cv2.line(image, bottomRight, bottomLeft, bottom_color, 3)
                cv2.line(image, bottomLeft, topLeft, (255, 0, 0), 3)
                
        return image
    
def main():
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)
        
    while cap.isOpened():
    
        ret, img = cap.read()
        
        markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(img)
    
        detected_markers = aruco_display(markerCorners, markerIds, img)
    
        cv2.imshow("Markers", detected_markers)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    
    cv2.destroyAllWindows()
    cap.release()

main()