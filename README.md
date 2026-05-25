# my jank hand controller
*part of this readme was generated with ai*

A quick hand controller demo for showcasing its use with open-world games.

[Video showcase](https://youtu.be/gJG4LHdM47o)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lornzoe/fyp-test.git
   cd fyp-test
   ```

2. **Create a Virtual Environment (Recommended)**:
   ```bash
   python -m venv .venv
   # Activate on Windows:
   .\.venv\Scripts\activate
   ```

3. **Install Dependencies**:
   The project requires the libraries specified in `requirements.txt`.
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the Model**:
   Ensure `hand_landmarker.task` is placed in the same folder as `main.py`.

## Usage

Run the main script:
```bash
python main.py
```

To exit, press `Q` while focused on the webcam window.

## Project Notes 
### Keymaps and gestures
Keymaps are stored in mymaps.py. The gestures available here are based on the [HaGRIDv2 dataset](https://github.com/hukenovs/hagrid/), but without the 2-handed gestures (except for holy).

![gestures](https://github.com/hukenovs/hagrid/raw/master/images/gestures.png)

In mymaps.py, generally the format goes as:
```
'label': 'key' # this is generically going to trigger as keyDown('key') and keyUp('key')

# some other unique classifiers
'label': 'left_click' # pyautogui.mouseDown(button='left')
'label': 'right_click' # same thing
'label': 'controller' # hardcoded for the movement_controller
```


While the model was trained with all the gestures listed here, in practice some gestures were not trained as well as others, and generally were not used: 

- point, grabbing, had a low precision score when testing
- mute was easy to trigger by accident
### Code flow

- Gestures in the current frame (and held for a minimum time) will have their corresponding keybind be put into a set keys_to_hold_this_frame.
- Every loop, the set is checked; incoming gestures will have their keys will be pressed with `pyautogui.keyDown()`
- Outgoing gestures (no longer present in webcam) will be released with `pyautogui.keyUp()`

A movement controller (movement_controller()) was made with extra logic to use the same gesture (gun) for left-right inputs.
- gun for left/right movement -- point it to the corresponding direction for their respective input.
- Currently the gun, two_up and two_up_inv. gesture is hard-coded for this.

A mouse controller (mouse_controller()) was made to manipulate mouse movement in games. 
- Uses Python's built in ctypes
- The implementation is Windows only
- Requires the right hand to do the one gesture
   - This requirement is hard-coded, and also overrides any gesture keymap for 'one' on the right hand.

### Limitations / Current technical challenges

- Mouse controller
   - I wasn't able to get pyautogui, pynput, or pydirectinput to work for this.
      - This may be due to Wuthering Waves, gacha open-world games, using anticheat that may not allow these kinds of inputs (falls under scripting)
   - ctypes is Windows-specific.
   - I'm pretty sure this needs administrator permissions.

- Webcam setup
   - Unsure why exactly, but needed to add `cv2.CAP_DSHOW` when setting up the camera. Probably an issue on my end and I need to reinstall/reset Windows on my laptop. 
- Messy code
   - self explanatory, sorry.

## Other Information
### model_builder/
This folder contains the source code used to build hagridv2_gesture_recognizer.task, as well as evaluation reports (confusion matrix, precision, accuracy, recall, f1 scores)