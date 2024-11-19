import cv2
import mediapipe as mp

# Initialize Mediapipe hands and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Function to determine if hand is open
def is_open_hand(landmarks):
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Check if all fingers are above the base of the hand
    return (index_tip.y < thumb_tip.y and
            middle_tip.y < thumb_tip.y and
            ring_tip.y < thumb_tip.y and
            pinky_tip.y < thumb_tip.y)

# Function to determine if the gesture is a thumbs up
def is_thumbs_up(landmarks):
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    # Check if the thumb is extended and the index is down
    return (thumb_tip.y < index_tip.y)

# Function to determine if the gesture is a peace sign
def is_peace_sign(landmarks):
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Check if index and middle fingers are up while others are down
    return (index_tip.y < middle_tip.y and
            ring_tip.y > middle_tip.y and
            pinky_tip.y > middle_tip.y)


# Function to determine if the gesture is a two fingers up
def is_two_fingers_up(landmarks):
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # Check if index and middle fingers are up while others are down
    return (index_tip.y < thumb_tip.y and 
            middle_tip.y < thumb_tip.y and 
            ring_tip.y > thumb_tip.y and 
            pinky_tip.y > thumb_tip.y)

# Start video capture
cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture video.")
            break
        
        # Convert the frame to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Process the image and detect hands
        results = hands.process(image)
        
        # Convert back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Determine gesture
                if is_open_hand(hand_landmarks.landmark):
                    gesture_text = 'Open Hand'
                    gesture_color = (0, 255, 0)  # Green
                elif is_thumbs_up(hand_landmarks.landmark):
                    gesture_text = 'Thumbs Up'
                    gesture_color = (255, 255, 0)  # Cyan
                elif is_peace_sign(hand_landmarks.landmark):
                    gesture_text = 'Peace Sign'
                    gesture_color = (255, 0, 255)  # Magenta
                elif is_two_fingers_up(hand_landmarks.landmark):
                    gesture_text = 'Two Fingers Up'
                    gesture_color = (128, 0, 128)  # Purple
                else:
                    gesture_text = 'Fist'
                    gesture_color = (0, 0, 255)  # Red
                
                # Display gesture text on the image
                cv2.putText(image, gesture_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, gesture_color, 2)

        # Display the resulting frame
        cv2.imshow('Hand Gesture Detection', image)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the capture and destroy windows
cap.release()
cv2.destroyAllWindows()
