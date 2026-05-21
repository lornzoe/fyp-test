import mediapipe as mp
import cv2
import pyautogui
import time

from mymaps import GESTURE_PROFILES

# --- Configuration ---
TAP_THRESHOLD = 0.5
GESTURE_SCORE_THRESHOLD = 0.7
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# Tracking state
gesture_start_times = {}
held_keys = set()

# Global variables for rendering
latest_result = None

model_path = 'hagridv2_gesture_recognizer.task'

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# For Arknights: Endfield
# GESTURE_KEY_MAP = {
#     # 'Pointing_Up': 'w',
#     # 'Open_Palm': 'space',
#     # 'Thumb_Up': 'a',
#     # 'Thumb_Down': 'd',
#     # 'ILoveYou': 's',
#     # 'Victory': 'w'
# }

GESTURE_KEY_MAP = GESTURE_PROFILES.get('game', {})

# --- CUSTOM DRAWING FUNCTION ---
def draw_landmarks(image, result):
    if not result or not result.hand_landmarks:
        return
    
    h, w, _ = image.shape
    for hand_landmarks in result.hand_landmarks:
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
            (5, 6), (6, 7), (7, 8),         # Index
            (9, 10), (10, 11), (11, 12),    # Middle
            (13, 14), (14, 15), (15, 16),   # Ring
            (17, 18), (18, 19), (19, 20),   # Pinky
            (0, 5), (5, 9), (9, 13), (13, 17), (0, 17) # Palm connections
        ]
        
        points = []
        for lm in hand_landmarks:
            points.append((int(lm.x * w), int(lm.y * h)))
            
        for connection in connections:
            start_point = points[connection[0]]
            end_point = points[connection[1]]
            cv2.line(image, start_point, end_point, (255, 255, 255), 2)
            
        for pt in points:
            cv2.circle(image, pt, 5, (0, 255, 0), -1)


def movement_controller(gesture_name, landmarks):
    if gesture_name == 'two_up':
        return 'w'
    if gesture_name == 'two_up_inverted':
        return 's'
    if gesture_name == 'three_gun' and landmarks:
        wrist = landmarks[0]
        index_tip = landmarks[8]
        return 'a' if index_tip.x < wrist.x else 'd'
    return None


def print_result(result, output_image, timestamp_ms):
    global gesture_start_times, held_keys, latest_result
    latest_result = result
    
    current_time = timestamp_ms / 1000.0  
    detected_gestures = set()
    gesture_to_key = {}

    if result.gestures:
        # Check for emergency stop
        if any(g[0].category_name == 'Closed_Fist' and g[0].score >= GESTURE_SCORE_THRESHOLD for g in result.gestures):
            for key in list(held_keys): pyautogui.keyUp(key)
            held_keys.clear()
            gesture_start_times.clear()
            return

        for i, hand_gestures in enumerate(result.gestures):
            gesture = hand_gestures[0]
            if gesture.score < GESTURE_SCORE_THRESHOLD:
                continue

            gesture_name = gesture.category_name
            handedness = result.handedness[i][0].category_name 

            # if we detect a controller specific gesture, start up this bit
            if GESTURE_KEY_MAP.get(gesture_name) == 'controller':
                # init 
                landmarks = None
                if result.hand_landmarks and len(result.hand_landmarks) > i:
                    landmarks = result.hand_landmarks[i]
                # movement controller
                movement_key = movement_controller(gesture_name, landmarks)
                if movement_key:
                    gesture_to_key[gesture_name] = movement_key
                    detected_gestures.add(gesture_name)

            # default behaviour
            elif gesture_name in GESTURE_KEY_MAP:
                gesture_to_key[gesture_name] = GESTURE_KEY_MAP[gesture_name]
                detected_gestures.add(gesture_name)

    keys_to_hold_this_frame = set()
    for gesture in detected_gestures:
        base_key = gesture_to_key.get(gesture)
        if not base_key:
            continue
        if gesture not in gesture_start_times:
            gesture_start_times[gesture] = current_time
        else:
            duration = current_time - gesture_start_times[gesture]
            if duration >= TAP_THRESHOLD:
                keys_to_hold_this_frame.add(base_key)

    ended_gestures = set(gesture_start_times.keys()) - detected_gestures
    for gesture in ended_gestures:
        key_to_press = gesture_to_key.get(gesture) or GESTURE_KEY_MAP.get(gesture)
        if key_to_press and current_time - gesture_start_times[gesture] < TAP_THRESHOLD:
            pyautogui.press(key_to_press)
        del gesture_start_times[gesture]

    # Sync keys
    for key in (keys_to_hold_this_frame - held_keys):
        # exceptions
        if key == 'none': continue
        if key == 'controller': continue
        # explicit for clicks since they dont have keyDown
        if key == 'left_click':
            pyautogui.mouseDown()
        else:
            pyautogui.keyDown(key)
        held_keys.add(key)
        
    for key in list(held_keys - keys_to_hold_this_frame):
        if key == 'left_click':
            pyautogui.mouseUp()
        else:
            pyautogui.keyUp(key)
        held_keys.remove(key)

    pressed_keys = sorted(held_keys)
    print('Pressed keys:', pressed_keys)

    return pressed_keys

def main():
    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        num_hands=2,
        result_callback=print_result
    )

    recognizer = GestureRecognizer.create_from_options(options)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    success = cap.set(cv2.CAP_PROP_ZOOM, 0)

    if success:
        print("Zoom 0 set")
    else:
        print("Failed to adjust zoom.")
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int(time.perf_counter() * 1000)
        recognizer.recognize_async(mp_image, timestamp_ms)

        draw_landmarks(frame, latest_result)

        # --- UPDATED RENDERING BLOCK ---
        gesture_count = len(latest_result.gestures) if latest_result and latest_result.gestures else 0
        if latest_result and latest_result.gestures:
            for i, hand_gestures in enumerate(latest_result.gestures):
                gesture = hand_gestures[0]
                category_name = gesture.category_name
                score = round(gesture.score * 100, 2)
                handedness = "Unknown"
                if latest_result.handedness and len(latest_result.handedness) > i:
                    handedness = latest_result.handedness[i][0].category_name

                gesture_text = f"{handedness}: {category_name} ({score}%)"
                y = 90 + i * 30
                cv2.putText(frame, gesture_text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        pressed_text = 'Pressed: ' + (', '.join(sorted(held_keys)) if held_keys else 'none')
        cv2.putText(frame, pressed_text, (10, 90 + (gesture_count + 1) * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Webcam Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()
    for key in list(held_keys): pyautogui.keyUp(key)  

if __name__ == '__main__':
    main()