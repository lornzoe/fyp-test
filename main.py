import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import pydirectinput
import math

# State variables
game_mode = False # False = PyAutoGUI (Desktop), True = PyDirectInput (Games)
is_clicking = False
debug_landmarks = False

# Variables for smoothing the mouse movement
smoothening = 3
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

# Virtual trackpad area for tracking pointer
X_MIN, X_MAX = 0.25, 0.75 
Y_MIN, Y_MAX = 0.25, 0.75

WIDTH = 960
HEIGHT = 540

# calculation for virtual trackpad area, so that we don't have to do it every time
box_x1, box_y1 = int(X_MIN * WIDTH), int(Y_MIN * HEIGHT)
box_x2, box_y2 = int(X_MAX * WIDTH), int(Y_MAX * HEIGHT)
box_text = box_y1 - 10

# Mediapipe init
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

# Mouse manipulators init
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0
screen_width, screen_height = pyautogui.size()


# Setup OpenCV
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Error: Could not open webcam")
else:
    print("Webcam successfully initialized")

# optimisation
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

# defines

def draw_trackpad():
    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 255, 0), 2)
    cv2.putText(frame, "Trackpad", (box_x1, box_text), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

# Main loop
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Error hit, closing")
        break

    # Flip frame for mirror-like interaction
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        if debug_landmarks:
            for landmarks in detection_result.hand_landmarks:
                # Draw all 21 landmarks for debugging
                for i, landmark in enumerate(landmarks):
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                    # show joint numbers  
                    cv2.putText(frame, str(i), (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        landmarks = detection_result.hand_landmarks[0]

        # --- PRE-MOVEMENT CALCULATION ---
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance_sq = (index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2
        
        # Stabilization thresholds
        STABILIZE_THRESH = 0.005 # Freeze movement when fingers are close
        is_near_pinch = distance_sq < STABILIZE_THRESH

        # Gesture Check variables (Finger Pointing up)
        index_up = landmarks[8].y < landmarks[6].y
        middle_down = landmarks[12].y > landmarks[10].y
        ring_down = landmarks[16].y > landmarks[14].y
        pinky_down = landmarks[20].y > landmarks[18].y

        # Pixel coordinates for visual feedback (Index Tip)
        cx = int(landmarks[8].x * frame.shape[1])
        cy = int(landmarks[8].y * frame.shape[0])

        # --- MOVEMENT LOGIC ---
        # Added "and not is_near_pinch" to stop cursor movement when prepping a click
        if index_up and middle_down and ring_down and pinky_down and not is_near_pinch:
            
            # Map hand coordinates to the Active Zone
            hand_x = landmarks[8].x
            hand_y = landmarks[8].y

            rel_x = (hand_x - X_MIN) / (X_MAX - X_MIN)
            rel_y = (hand_y - Y_MIN) / (Y_MAX - Y_MIN)

            # Clamp the values so it doesn't break if hand leaves the box
            rel_x = max(0, min(1, rel_x))
            rel_y = max(0, min(1, rel_y))

            target_x = screen_width * rel_x
            target_y = screen_height * rel_y

            # Smooth the movement
            curr_x = prev_x + (target_x - prev_x) / smoothening
            curr_y = prev_y + (target_y - prev_y) / smoothening

            # Execute Movement
            try:
                if game_mode:
                    pydirectinput.moveTo(int(curr_x), int(curr_y))
                else:
                    pyautogui.moveTo(curr_x, curr_y)
            except (pyautogui.FailSafeException, pydirectinput.FailSafeException):
                print("Failsafe triggered! Mouse hit the corner.")
                break

            prev_x, prev_y = curr_x, curr_y

            # Draw purple tracking circle when moving
            cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        
        elif is_near_pinch:
            # Show yellow circle to indicate "Locked/Stabilized" mode
            cv2.circle(frame, (cx, cy), 10, (0, 255, 255), cv2.FILLED)

        # --- CLICKING LOGIC ---
        # 0.05**2 because why are we 
        if distance_sq < 0.0025:
            # Draw green tracking circle when clicking
            cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            
            if not is_clicking: # Trigger click only once per pinch
                if game_mode: # spam click
                    pydirectinput.mouseDown() 
                    pydirectinput.mouseUp()
                else: # once its pinched, hold pinch until its released
                    pyautogui.click()
                is_clicking = True
                print("Click")
        else:
            if is_clicking:
                print("Release Click")
            is_clicking = False

    # General UI overlay
    mode_text = "MODE: PyDirectInput" if game_mode else "MODE: PyAutoGUI"
    color = (0, 0, 255) if game_mode else (255, 0, 0)
    
    cv2.putText(frame, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, "Press 'm' to toggle modes | 'ESC' to quit", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    draw_trackpad()
    cv2.imshow('my jank hand tracker', frame)
    
    # KEY LISTENERS
    key = cv2.waitKey(1) & 0xFF
    if key == 27: # 27 is ESC
        print("Exiting")
        break
    elif key == ord('x'):
        debug_landmarks = not debug_landmarks
        print("Toggled debug_landmarks")
    elif key == ord('m'):
        game_mode = not game_mode
        print(f"Switched mode, game_mode is now: {game_mode}")

# Cleanup
cap.release()
cv2.destroyAllWindows()