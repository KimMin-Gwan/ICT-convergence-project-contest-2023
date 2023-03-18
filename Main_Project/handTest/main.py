import cv2
import mediapipe as mp
import numpy as np
import hand

cap = cv2.VideoCapture(0)
 
def main():
    init = False
    trigger = False
    hands_data = None

    if init is False:
        hands_data, count, init, now_dist = hand.hand_gesture(init)

    while True:
        ret, image = cap.read(0)
        if not ret :
            print('no camera')
            continue

        if trigger is True:

            image, gesture, count, now_dist = hand.check_trigger(image, hands_data, count, now_dist)

            if gesture == True:
                print('main gestrue detected')

        cv2.imshow('medoaPip hands', cv2.flip(image, 1))

        if cv2.waitKey(5) & 0xFF == 27:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if trigger is True:
                trigger = False
                init = False
            else:
                trigger = True


    cap.release()



if __name__ == '__main__':
    main()