import numpy as np
import hand

def get_coords(component):
    x = component.x
    y = component.y
    return x, y

def check_gesture(thumb, index, now_dist):
    x_2 = (thumb[0] - index[0]) ** 2
    y_2 = (thumb[1] - index[1]) ** 2
    new_dist = np.sqrt(x_2 + y_2)

    if new_dist > now_dist + 0.001:
        print('True : ', new_dist)
        return 1, new_dist, True
    print('false : ', new_dist )
    return 0, new_dist, False

def hand_gesture():
    hands =  hand.mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    hands_data = hands
    count = 0
    now_dist = 0
    return hands_data, count, now_dist
