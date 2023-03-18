import numpy as np
import hand
#import mediapipe as mp

def get_coords(component):
    x = component.x
    y = component.y
    return x, y

def check_gesture(thumb, index, now_dist):
    x_2 = (thumb[0] - index[0]) ** 2
    y_2 = (thumb[1] - index[1]) ** 2
    new_dist = np.sqrt(x_2 + y_2)
    print('now_dist : ', now_dist)

    if new_dist > now_dist + 0.001:
        print('True : ', new_dist)
        return 1, new_dist, True

    print('false : ', new_dist )
    return 0, new_dist, False

def hand_gesture(inital):
    hands =  hand.mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    hands_data = hands
    inital = True
    count = 0
    now_dist = 0
    return hands_data, count, inital, now_dist

"""
class HandsData:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

def hand_gesture(init):
    if init is True:
        return None

    hands_data = HandsData()
    init = True
    count = 0
    now_dist = 0

    return hands_data, count, init, now_dist

"""