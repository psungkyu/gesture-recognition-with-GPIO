import cv2
import mediapipe as mp
import time
import RPi.GPIO as GPIO
from enum import Enum

class LED_PIN(Enum):
    RED = 17
    YELLOW = 27
    GREEN = 22
    
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN.RED.value, GPIO.OUT) #Red
GPIO.setup(LED_PIN.YELLOW.value, GPIO.OUT) #Yellow
GPIO.setup(LED_PIN.GREEN.value, GPIO.OUT) #Green

def led_dimming(duration=5, pwm_frequency=100):
    pwm = GPIO.PWM(LED_PIN.RED.value, pwm_frequency)
    pwm2 = GPIO.PWM(LED_PIN.YELLOW.value, pwm_frequency)
    pwm3 = GPIO.PWM(LED_PIN.GREEN.value, pwm_frequency)

    try:
        pwm.start(0)
        pwm2.start(0)
        pwm3.start(0)
        
        for duty_cycle in range(0, 51, 5):
            pwm.ChangeDutyCycle(duty_cycle)
            pwm2.ChangeDutyCycle(duty_cycle)
            pwm3.ChangeDutyCycle(duty_cycle)
            time.sleep(10 / (pwm_frequency * 2))
                
        for duty_cycle in range(50,-5, -5):
            pwm.ChangeDutyCycle(duty_cycle)
            pwm2.ChangeDutyCycle(duty_cycle)
            pwm3.ChangeDutyCycle(duty_cycle)
            time.sleep(10 / (pwm_frequency * 2))
            
    finally:
        pwm.stop()
        pwm2.stop()
        pwm3.stop()
        
# 손가락 개수 세기 함수
def count_fingers(hand_landmarks):
    finger_tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
    count = 0
    for finger_tip in finger_tips:
        if hand_landmarks.landmark[finger_tip].y < hand_landmarks.landmark[finger_tip-1].y:
            count += 1
    return count

hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            finger_count = count_fingers(hand_landmarks)
            
            # 손가락 끝이 PIP보다 위에 있고 엄지손가락 끝이 IP보다 오른쪽에 있는 경우
            if (hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y) and (hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x > hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x) and (finger_count == 3):
                print("Okay!")

            # 손가락 개수가 4개인 경우
            elif count_fingers(hand_landmarks) == 4:
                print("palm detection!")
            
            elif (hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].y) and (hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].x > hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x):
                print("Let's go surfing!")
                led_dimming()
                
                
            # 손가락 개수 출력
            if finger_count > 0:
                print("count of finger is " + str(finger_count))
                if finger_count == 3:
                    GPIO.output(LED_PIN.RED.value, True)
                    GPIO.output(LED_PIN.YELLOW.value, True)
                    GPIO.output(LED_PIN.GREEN.value, True)
                elif finger_count == 2:
                    GPIO.output(LED_PIN.RED.value, True)
                    GPIO.output(LED_PIN.YELLOW.value, True)
                    GPIO.output(LED_PIN.GREEN.value, False)
                elif finger_count == 1:
                    GPIO.output(LED_PIN.RED.value, True)
                    GPIO.output(LED_PIN.YELLOW.value, False)
                    GPIO.output(LED_PIN.GREEN.value, False)
                else:
                    GPIO.output(LED_PIN.RED.value, False)
                    GPIO.output(LED_PIN.YELLOW.value, False)
                    GPIO.output(LED_PIN.GREEN.value, False)

        #cv2.imshow('MediaPipe Hands', frame)
        #if cv2.waitKey(5) & 0xFF == 27:
         #   print("2")
         #   break

finally:
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()
