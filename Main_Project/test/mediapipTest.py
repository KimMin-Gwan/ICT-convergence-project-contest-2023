import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
min_count_move = 4

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

    

# 웹캠, 영상 파일의 경우 이것을 사용하세요.:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    count = 0
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("카메라를 찾을 수 없습니다.")
            continue

        thumb_tip = None
        index_tip = None
        # 필요에 따라 성능 향상을 위해 이미지 작성을 불가능함으로 기본 설정합니다.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 엄지 손가락 랜드마크 추출
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
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

            if (count >= min_count_move):
                gesture = True       
        

        # 이미지에 손 주석을 그립니다.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        #보기 편하게 이미지를 좌우 반전합니다.
        if gesture == True:
            print('gesture detected')
            count = 0

        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
