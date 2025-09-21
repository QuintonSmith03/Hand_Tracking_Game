import cv2
import mediapipe as mp


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

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Open default webcam for hand tracking
capture = cv2.VideoCapture(0)

if not capture.isOpened():
    raise RuntimeError("Could not open webcam. Ensure a camera is connected and accessible.")

prev_input = None

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame from webcam. Exiting.")
            break

        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detected_image = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        current_inputs = []

        if detected_image.multi_hand_landmarks:
            for hand_lms in detected_image.multi_hand_landmarks:
                current_inputs.append(hand_open_state(hand_lms))
                mp_drawing.draw_landmarks(
                    image,
                    hand_lms,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                        color=(255, 0, 255), thickness=4, circle_radius=2
                    ),
                    connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                        color=(20, 180, 90), thickness=2, circle_radius=2
                    ),
                )

        display_value = current_inputs[0] if current_inputs else None
        if display_value is not None:
            cv2.putText(
                image,
                f'Input: {display_value}',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        if display_value is not None and display_value != prev_input:
            print(f"Detected input: {display_value}")
            prev_input = display_value
        elif display_value is None:
            prev_input = None

        cv2.imshow('Webcam', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

capture.release()
cv2.destroyAllWindows()
