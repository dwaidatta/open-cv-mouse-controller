# Hand Mouse Controller

A Python project that lets you control your mouse cursor and perform mouse actions using your hand gestures via webcam, powered by OpenCV, MediaPipe, and PyAutoGUI.

This repository contains two main scripts:

- `hand.py`: Single-hand mouse controller (move, left/right click, scroll)
- `2hand.py`: Two-hand mouse controller (one hand for movement, the other for actions; always-on-top window)

---

## Table of Contents

- [Features](#features)
- [Setup & Installation](#setup--installation)
- [How It Works](#how-it-works)
  - [hand.py](#handpy-single-hand-mode)
  - [2hand.py](#2handpy-two-hand-mode)
- [Parameters Explained](#parameters-explained)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- **Hand gesture-based mouse movement**
- **Left and right click** via finger pinching
- **Smooth and responsive scrolling** with hand gestures
- **Two-hand mode**: Separate hands for movement and actions
- **Always-on-top camera window** (Windows only in `2hand.py`)
- **Minimal hand movement required** for full screen control

---

## Setup & Installation

### 1. Clone the Repository

`git clone https://github.com/dwaidatta/open-cv-mouse-controller.git`

`cd hand-mouse-controller`


### 2. Install Python Dependencies

`pip install opencv-python mediapipe pyautogui numpy`

#### For Windows Always-on-Top Feature (in `2hand.py`):

`pip install pygetwindow pywin32`

---

## How It Works

### `hand.py`: Single-Hand Mode

- **Controls movement and actions with one hand.**
- **Mouse movement:** Move your index finger; cursor follows with acceleration and smoothing.
- **Left click:** Pinch index and middle fingers together.
- **Right click:** Pinch index and ring fingers together.
- **Scroll:** Hold index and middle fingers up and apart, then move hand up/down.

#### **Code Structure**

- **Imports:** Loads OpenCV, MediaPipe, PyAutoGUI, NumPy.
- **Video Capture:** Opens webcam and sets frame size.
- **Hand Detection:** Uses MediaPipe to detect one hand and track landmarks.
- **Parameters:**  
  - `ACCELERATION`: Speed multiplier for cursor movement.
  - `SMOOTHING`: Blends new/old movement to reduce jitter.
  - `MOVEMENT_THRESHOLD`: Minimum movement to trigger cursor move.
- **Gesture Detection:**
  - `fingers_up()`: Detects which fingers are up.
  - `distance()`: Calculates Euclidean distance between two landmarks.
- **Main Loop:**
  - Reads frame, flips horizontally for natural control.
  - Detects hand landmarks.
  - Moves mouse if index finger moves enough.
  - Checks for pinch gestures for left/right click.
  - Checks for scroll gesture and moves scroll wheel accordingly.
  - Draws hand landmarks and shows camera window.
- **Exit:** Press `ESC` to quit.

---

### `2hand.py`: Two-Hand Mode

- **Left hand:** Controls only mouse movement.
- **Right hand:** Controls only actions (left/right click, scroll).
- **Always-on-top window:** Keeps the camera feed window visible above all others (Windows only).

#### **Code Structure**

- **Additional Imports:**  
  - `pygetwindow`, `win32con`, `win32gui` for window management (Windows).
- **Hand Assignment:**  
  - When two hands detected, assigns left/right by comparing x-coordinates of index finger tips.
  - When one hand detected, assigns by position in frame.
- **Left Hand Logic:**  
  - Moves cursor if index finger moves more than `MOVEMENT_THRESHOLD`.
- **Right Hand Logic:**  
  - **Left click:** Pinch index and middle fingers.
  - **Right click:** Pinch index, middle, and ring fingers.
  - **Scroll:** All four fingers up (open hand), move hand up/down to scroll.
- **Always-on-top Window:**  
  - Uses `pygetwindow` and `win32gui` to keep the OpenCV window on top of all others.
- **Exit:** Press `ESC` to quit.

---

## Parameters Explained

| Parameter           | Description                                                                                  |
|---------------------|----------------------------------------------------------------------------------------------|
| `ACCELERATION`      | Multiplies hand movement to increase cursor speed. Higher = faster cursor.                   |
| `SMOOTHING`         | Blends previous and current movement for stability. 0 = no smoothing, 1 = max smoothing.     |
| `MOVEMENT_THRESHOLD`| Minimum pixel movement needed to move cursor (filters out jitter/noise).                     |

---

## Usage

1. **Run the script:**

`python hand.py`

or

`python 2hand.py`

2. **Control the mouse with your hand(s):**

- **hand.py:** Use one hand for both movement and actions.
- **2hand.py:** Use left hand for movement, right hand for actions.

3. **Gestures:**

| Action         | hand.py Gesture                | 2hand.py Gesture (Right Hand)         |
|----------------|-------------------------------|---------------------------------------|
| Move Cursor    | Move index finger             | Move left hand index finger           |
| Left Click     | Pinch index + middle          | Pinch index + middle                  |
| Right Click    | Pinch index + ring            | Pinch index + middle + ring           |
| Scroll         | Index + middle up/apart, move | Open hand (all fingers up), move up/down |

4. **Exit:** Press `ESC`.

---

## Troubleshooting

- **Jittery cursor:** Increase `MOVEMENT_THRESHOLD` or `SMOOTHING`.
- **Cursor too slow/fast:** Adjust `ACCELERATION`.
- **Window not always on top:** The always-on-top feature works only on Windows and requires `pygetwindow` and `pywin32`.
- **Hand not detected:** Ensure good lighting and keep your hand within webcam frame.

---

## License

This project is open source and free to use for personal and educational purposes.

---

## Credits

- [OpenCV](https://opencv.org/)
- [MediaPipe](https://google.github.io/mediapipe/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)
- [pygetwindow](https://github.com/asweigart/PyGetWindow)
