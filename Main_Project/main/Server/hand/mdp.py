import hand
from hand.utils import get_coords, check_gesture
import cv2
import numpy as np

def check_trigger(image, hands, count, now_dist):
    thumb_tip = None
    index_tip = None
    # 필요에 따라 성능 향상을 위해 이미지 작성을 불가능함으로 기본 설정합니다.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 엄지 손가락 랜드마크 추출
            thumb_tip = hand_landmarks.landmark[hand.mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[hand.mp_hands.HandLandmark.INDEX_FINGER_TIP]
    #thumb_tip = np.array([thumb_tip.x, thumb_tip.y])
    gesture = False 
    flag = False
    if thumb_tip is not None and index_tip is not None:
        thumb_xy = np.array(get_coords(thumb_tip))
        index_xy = np.array(get_coords(index_tip))
        if count == 0:
            adder, now_dist, flag = check_gesture(thumb_xy, index_xy, 0)
        else :
            adder, now_dist, flag = check_gesture(thumb_xy, index_xy, now_dist)

        if flag == True:
            count += adder
        elif flag == False:
            count = 0

        if (count >= hand.min_count_move):
            gesture = True       
    

    # 이미지에 손 주석을 그립니다.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hand.mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                hand.mp_hands.HAND_CONNECTIONS,
                hand.mp_drawing_styles.get_default_hand_landmarks_style(),
                hand.mp_drawing_styles.get_default_hand_connections_style())
    #보기 편하게 이미지를 좌우 반전합니다.
    if gesture == True:
        print('gesture detected')
        count = 0

    image = cv2.flip(image, 1)

    return image, gesture, count, now_dist
    

