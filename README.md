# my jank hand controller
*part of this readme was generated with ai*
A quick hand controller demo to utilise mouse control (navigation, click) using OpenCV and Mediapipe.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lornzoe/fyp-test.git
   cd your-repo-name
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   # Activate on Windows:
   .\.venv\Scripts\activate
   ```

3. **Install Dependencies**:
   The project requires the libraries specified in `requirements.txt`, including MediaPipe, OpenCV, PyAutoGUI, and PyDirectInput.
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

### Keybindings
* **`m`**: Toggle between PyAutoGUI (Desktop) and PyDirectInput (Game) modes.
* **`x`**: Toggle Debug Mode (shows hand landmark indices).
* **`ESC`**: Exit the application safely.

### Gestures
* **Cursor Movement**: Extend your **Index Finger** within the yellow "Trackpad" box.
* **Left Click**: Pinch your **Thumb** and **Index Finger** together (Tracking circle turns green).
* **Stabilize/Lock**: Bring your thumb close to your index finger (Tracking circle turns yellow) to freeze the cursor position for precise clicking.
