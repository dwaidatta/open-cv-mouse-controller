import cv2
import mediapipe as mp
import pyautogui
import numpy as np

pyautogui.FAILSAFE = False

cap = cv2.VideoCapture(0)
FRAME_W, FRAME_H = 640, 480
cap.set(3, FRAME_W)
cap.set(4, FRAME_H)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75)
mp_draw = mp.solutions.drawing_utils

# Parameters
ACCELERATION = 8
SMOOTHING = 0
MOVEMENT_THRESHOLD = 3  # pixels; increase if you still see jitter

prev_x, prev_y = None, None
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

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        lm_list = hand_landmarks.landmark

        # Get index finger tip position
        finger_x = int(lm_list[8].x * FRAME_W)
        finger_y = int(lm_list[8].y * FRAME_H)

        if prev_x is not None and prev_y is not None:
            dx = finger_x - prev_x
            dy = finger_y - prev_y

            # Only move mouse if movement is above threshold to avoid jitter[2]
            if abs(dx) > MOVEMENT_THRESHOLD or abs(dy) > MOVEMENT_THRESHOLD:
                velocity_x = velocity_x * SMOOTHING + (dx * ACCELERATION) * (1 - SMOOTHING)
                velocity_y = velocity_y * SMOOTHING + (dy * ACCELERATION) * (1 - SMOOTHING)
                pyautogui.move(velocity_x, velocity_y)

        prev_x, prev_y = finger_x, finger_y

        # Gesture detection
        fingers = fingers_up(hand_landmarks)
        pinch_distance = distance(lm_list[8], lm_list[12])  # Index to middle
        pinch_distance_ring = distance(lm_list[8], lm_list[16])  # Index to ring

        # Left click: pinch index and middle fingers
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            if pinch_distance < 0.045:
                if not click_down:
                    pyautogui.click()
                    click_down = True
            else:
                click_down = False
        else:
            click_down = False

        # Right click: pinch index and ring fingers
        if fingers[1] and fingers[3] and not fingers[2] and not fingers[4]:
            if pinch_distance_ring < 0.045:
                if not right_click_down:
                    pyautogui.click(button='right')
                    right_click_down = True
            else:
                right_click_down = False
        else:
            right_click_down = False

        # Scroll mode: index and middle fingers up and apart, move up/down
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            if pinch_distance > 0.08:
                if not scroll_mode:
                    scroll_mode = True
                    scroll_start_y = finger_y
                else:
                    scroll_diff = finger_y - scroll_start_y
                    if abs(scroll_diff) > 5:  # Lowered threshold for easier scrolling
                        pyautogui.scroll(-int(scroll_diff * 2))  # More sensitive scroll
                        scroll_start_y = finger_y
            else:
                scroll_mode = False
        else:
            scroll_mode = False

        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Accelerated Hand Mouse", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
