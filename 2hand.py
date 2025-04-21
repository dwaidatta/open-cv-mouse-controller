import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import pygetwindow as gw
import win32con
import win32gui

pyautogui.FAILSAFE = False

cap = cv2.VideoCapture(0)
FRAME_W, FRAME_H = 640, 480 
cap.set(3, FRAME_W)
cap.set(4, FRAME_H)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.75)
mp_draw = mp.solutions.drawing_utils

ACCELERATION = 8
SMOOTHING = 0
MOVEMENT_THRESHOLD = 1

prev_left_x, prev_left_y = None, None
velocity_x, velocity_y = 0, 0

click_down = False
right_click_down = False
scroll_mode = False
scroll_start_y = 0

def fingers_up(hand_landmarks):
    tips_ids = [4, 8, 12, 16, 20]
    fingers = []
    # Thumb
    fingers.append(hand_landmarks.landmark[tips_ids[0]].x < hand_landmarks.landmark[tips_ids[0] - 1].x)
    # Fingers
    for id in range(1, 5):
        fingers.append(hand_landmarks.landmark[tips_ids[id]].y < hand_landmarks.landmark[tips_ids[id] - 2].y)
    return fingers

def distance(lm1, lm2):
    return np.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    left_hand_landmarks = None
    right_hand_landmarks = None

    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
        hand0 = results.multi_hand_landmarks[0]
        hand1 = results.multi_hand_landmarks[1]
        x0 = hand0.landmark[8].x
        x1 = hand1.landmark[8].x
        if x0 < x1:
            left_hand_landmarks = hand0
            right_hand_landmarks = hand1
        else:
            left_hand_landmarks = hand1
            right_hand_landmarks = hand0
    elif results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 1:
        hand = results.multi_hand_landmarks[0]
        if hand.landmark[8].x < 0.5:
            left_hand_landmarks = hand
        else:
            right_hand_landmarks = hand

    # Mouse movement with left hand only
    if left_hand_landmarks is not None:
        lm_list = left_hand_landmarks.landmark
        finger_x = int(lm_list[8].x * FRAME_W)
        finger_y = int(lm_list[8].y * FRAME_H)
        if prev_left_x is not None and prev_left_y is not None:
            dx = finger_x - prev_left_x
            dy = finger_y - prev_left_y
            if abs(dx) > MOVEMENT_THRESHOLD or abs(dy) > MOVEMENT_THRESHOLD:
                velocity_x = velocity_x * SMOOTHING + (dx * ACCELERATION) * (1 - SMOOTHING)
                velocity_y = velocity_y * SMOOTHING + (dy * ACCELERATION) * (1 - SMOOTHING)
                pyautogui.move(velocity_x, velocity_y)
        prev_left_x, prev_left_y = finger_x, finger_y
        mp_draw.draw_landmarks(img, left_hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Mouse actions with right hand only
    if right_hand_landmarks is not None:
        lm_list = right_hand_landmarks.landmark
        fingers = fingers_up(right_hand_landmarks)
        pinch_distance = distance(lm_list[8], lm_list[12])  # Index to middle
        pinch_distance_ring = distance(lm_list[8], lm_list[16])  # Index to ring

        # Left click: index + middle pinch
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            if pinch_distance < 0.045:
                if not click_down:
                    pyautogui.click()
                    click_down = True
            else:
                click_down = False
        else:
            click_down = False

        # Right click: index + middle + ring pinch
        if fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
            if pinch_distance < 0.045 and pinch_distance_ring < 0.045:
                if not right_click_down:
                    pyautogui.click(button='right')
                    right_click_down = True
            else:
                right_click_down = False
        else:
            right_click_down = False

        # Scroll: only when right hand is open (all fingers up except thumb)
        if fingers[1] and fingers[2] and fingers[3] and fingers[4]:
            finger_y = int(lm_list[8].y * FRAME_H)
            if not scroll_mode:
                scroll_mode = True
                scroll_start_y = finger_y
            else:
                scroll_diff = finger_y - scroll_start_y
                if abs(scroll_diff) > 5:
                    pyautogui.scroll(-int(scroll_diff * 6))
                    scroll_start_y = finger_y
        else:
            scroll_mode = False

        mp_draw.draw_landmarks(img, right_hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Two Hand Mouse Controller", img)
    # Keep window always on top
    window_title = "Two Hand Mouse Controller"
    try:
        win = gw.getWindowsWithTitle(window_title)[0]
        win32gui.SetWindowPos(
            win._hWnd, win32con.HWND_TOPMOST,
            win.left, win.top, win.width, win.height,
            0
        )
    except IndexError:
        pass
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
