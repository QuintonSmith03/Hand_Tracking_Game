import cv2
import mediapipe as mp
import pyautogui


#Mouse input function

def mouse_input(display_value):
    if display_value == 0:
        pyautogui.mouseDown()

    if display_value == 1:
        pyautogui.mouseUp()




screen_w, screen_h = pyautogui.size()  # Screen size
smoothed_x = screen_w / 2
smoothed_y = screen_h / 2


def mouse_position(wrist_point):
    """Smoothly move the cursor toward the wrist coordinates."""
    global smoothed_x, smoothed_y

    wrist_x = wrist_point.x * screen_w
    wrist_y = wrist_point.y * screen_h

    alpha = 0.7  # smoothing factor
    smoothed_x = alpha * smoothed_x + (1 - alpha) * wrist_x
    smoothed_y = alpha * smoothed_y + (1 - alpha) * wrist_y

    pyautogui.moveTo(int(smoothed_x), int(smoothed_y))


def hand_open_state(hand_landmarks):
    """Return 1 when most fingers appear extended, otherwise 0."""
    finger_tip_ids = [8, 12, 16, 20]
    finger_pip_ids = [6, 10, 14, 18]

    extended_fingers = 0
    for tip_id, pip_id in zip(finger_tip_ids, finger_pip_ids):
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[pip_id]
        if tip.y < pip.y:
            extended_fingers += 1

    return 1 if extended_fingers >= 3 else 0

mp_hands = mp.solutions.hands

# Open default webcam for hand tracking
capture = cv2.VideoCapture(0)

#Optimization fixes 
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

prev_input = None
prev_raw_input = None
stable_count = 0


with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5, model_complexity=0, max_num_hands=1) as hands:
    while capture.isOpened():
        ret, frame = capture.read()

        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detected_image = hands.process(image)

        display_value = None

        if detected_image.multi_hand_landmarks:
            for hand_lms in detected_image.multi_hand_landmarks:
                display_value = hand_open_state(hand_lms)
                wrist = hand_lms.landmark[mp_hands.HandLandmark.WRIST]
                mouse_position(wrist)
                break  # Only one hand needed for cursor control

        if display_value is not None:
            if display_value == prev_raw_input:
                stable_count += 1
            else:
                prev_raw_input = display_value
                stable_count = 1

            if stable_count >= 3 and display_value != prev_input:
                print(f"Detected input: {display_value}")
                mouse_input(display_value)
                prev_input = display_value
        else:
            prev_raw_input = None
            stable_count = 0
            prev_input = None

       # cv2.imshow('Webcam', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

capture.release()
# cv2.destroyAllWindows()
