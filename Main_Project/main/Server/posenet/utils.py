import cv2 
import numpy as np  

import posenet.constants


# 유효한 해상도를 계산하는 함수
# 입력 : 이미지의 너비(width), 높이(height), 출력 스트라이드(output_stride)
def valid_resolution(width, height, output_stride=16):

    # 유효한 해상도 계산
    target_width = (int(width) // output_stride) * output_stride + 1
    target_height = (int(height) // output_stride) * output_stride + 1

    # 반환값은 (target_width, target_height) 형태의 튜플로 반환
    return target_width, target_height


# 입력 이미지를 처리하는 함수 
# 입력 이미지는 source_img로 제공, scale_factor와 output_stride 매개변수를 사용하여 이미지를 전처리
def _process_input(source_img, scale_factor=1.0, output_stride=16):

    # valid_resolution 함수를 통해 유효한 해상도를 계산
    target_width, target_height = valid_resolution(
        source_img.shape[1] * scale_factor, source_img.shape[0] * scale_factor, output_stride=output_stride)
    
    # scale = 이미지를 처리하기 위해 사용되는 크기 비율
    # 축소된 비율을 이용해 배열 만들고 이를 이용해 후속 처리 단계에서 원하는 크기로 확장 
    scale = np.array([source_img.shape[0] / target_height, source_img.shape[1] / target_width])
    #print('target_width = ', target_width)
    #print('target_height = ', target_height)
    
    # cv2의 resize함수를 이용하여 source_img를 target_width와 target_height에 맞게 조정
    # resize 함수 = 이미지의 크기를 조절하는 함수 
    # cv2.INTER_LINEAR 함수 = 양선형 보간법 (효율성이 가장 좋음, 속도 빠름, 퀄리티 적당)
    input_img = cv2.resize(source_img, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
    
    # cv2의 cvtColor함수를 이용하여 BGR 색상 공간에서 RGB 색상 공간으로 변환
    input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB).astype(np.float32)
    
    # 이미지를 픽셀 단위로 정규화 (픽셀 범위 : 0 ~ 255 -> -1 ~ 1)
    input_img = input_img * (2.0 / 255.0) - 1.0

    # reshape함수를 이용하여 4차원을 가지는 배열로 변환
    # 첫번째 차원 : 배치 크기 (하나의 이미지만 처리하므로 1) / 두번째, 세번째 차원 : 이미지의 높이와 너비 / 네번째 차원 : 색상 채널
    input_img = input_img.reshape(1, target_height, target_width, 3)
    
    # 반환값은 전처리된 입력 이미지(input_img), 원본 입력 이미지(source_img), 크기 조정시 사용된 크기 비율(scale)
    return input_img, source_img, scale


# 웹캠에서 읽은 영상 프레임을 입력으로 받아 함수 호출을 통한 처리 후 반환하는 함수
def read_cap(cap, scale_factor=1.0, output_stride=16):

    # cap.read 함수를 이용하여 프레임을 읽어오기
    # 비디오 프레임을 제대로 읽으면 res가 true, 실패시 false  / 읽은 프레임은 img

    # 반환값은 읽은 이미지를 함수를 통해 처리한 값    
    return _process_input(cap, scale_factor, output_stride)


# 점의 좌표를 가지고 오는 함수 (연결된 키포인트들의 좌표를 계산)
def get_adjacent_keypoints(keypoint_scores, keypoint_coords, min_confidence=0.1):
    results = [] #리턴시킬 배열 (x, y)
    
    # posenet에서 받아온 인덱스들의 좌 우를 찍음
    # posenet.CONNECTED_PART_INDICES는 연결된 키포인트 쌍들을 나타내는 상수
    for left, right in posenet.CONNECTED_PART_INDICES:
        if keypoint_scores[left] < min_confidence or keypoint_scores[right] < min_confidence:
            continue
        
        #받아온 결과를 numpy.array 형식으로 [y, x] 와 같이 저장 (::의 역할 / opencv에서는 좌표값을 y,x 순서로 다룸)
        results.append(
            np.array([keypoint_coords[left][::-1], keypoint_coords[right][::-1]]).astype(np.int32),
        )
   
    # 반환값은 좌표값 
    return results


# 부위를 화면에 표시해주는 함수
def draw_part_name(
        img, instance_scores, keypoint_scores, keypoint_coords,
        min_pose_score = 0.5, min_part_score=0.5):
    out_img = img
    trigger = False
    font = cv2.FONT_HERSHEY_SIMPLEX
    real_co = []
    leftWrist = 0
    rightWrist = 0
    nose = 0
    
    for ii, score in enumerate(instance_scores):


        # score가 뭘 하는지 모르겠지만 아래 함수에서 써서 같이 써줌
        if score < min_pose_score:
            continue
        
        # instance_scores의 길이는 포즈 갯수와 같음
        for ki in range(len(instance_scores)):
            if instance_scores[ki] == 0.:
                break
            
            # x와 y가 뒤집혀 있어서 뒤집어서 real_co 배열에 넣어줌
            for kc, (s, c) in enumerate(zip(keypoint_scores[ki, :], keypoint_coords[ki, :, :])):
                name = posenet.PART_NAMES[kc]
                x = c[1].astype(np.int32)
                real_co.append(x)
                y = c[0].astype(np.int32)
                real_co.append(y)

                # 파트가 실제로 화면에 찍혔을때
                if s > min_part_score :
                    # 화면에 출력
                    cv2.putText(out_img, name, real_co, font, 1, (0, 0, 0), 1 ) 
                    # 화면에 잡힌 손과 코의 y좌표를 저장
                    if name == posenet.PART_NAMES[0]:
                        nose = y
                    elif name == posenet.PART_NAMES[9]:
                        leftWrist = y
                    elif name == posenet.PART_NAMES[10]:
                        rightWrist = y
                # 배열 비우기
                real_co.clear()
    # 만약 왼손과 오른손이 화면에 잡히고
    if leftWrist and rightWrist != 0:
        # 두 손중 하나가 코 위에 있다면 아래의 코드를 실행한다.
        if leftWrist < nose or rightWrist < nose :
            print('hand is higher than nose now')
            trigger = True

    return out_img, trigger

# 입력 이미지 위에 PoseNet 알고리즘이 예측한 결과를 시각화하여 출력 이미지를 반환하는 함수
# 위의 함수와 차이점은 좌표 표시 유무로 보임
def draw_skel_and_kp(
        img, instance_scores, keypoint_scores, keypoint_coords,
        min_pose_score=0.5, min_part_score=0.5):
    # 글꼴 설정
    font=cv2.FONT_HERSHEY_SIMPLEX

    out_img = img
    adjacent_keypoints = []
    cv_keypoints = []
    component = []

    coord = []

    # 01. get_adjacent...함수를 사용하여 이웃 키포인트 쌍의 목록을 가져오기
    for ii, score in enumerate(instance_scores):
        if score < min_pose_score:
            continue

        new_keypoints = get_adjacent_keypoints(
            keypoint_scores[ii, :], keypoint_coords[ii, :, :], min_part_score)
        
        adjacent_keypoints.extend(new_keypoints) # --- 여기까지가 위의 함수와 동일한 부분

        # 02. drawKeypoints 및 polylines를 사용하여 이웃하는 키포인트끼리 연결하는 뼈대 그리고 좌표 표시하기
        for ks, kc in zip(keypoint_scores[ii, :], keypoint_coords[ii, :, :]):
            if ks < min_part_score:
                continue

            # 조건을 만족한 경우에만 component 리스트에 추가
            x = kc[1].astype(np.int32)
            y = kc[0].astype(np.int32)
            component.append(x)
            component.append(y)

            # cv2.KeyPoint 객체를 생성하여 cv_keypoints 리스트에 추가
            cv_keypoints.append(cv2.KeyPoint(kc[1], kc[0], 10. * ks))

        # component 리스트를 coord 리스트에 추가
        coord.extend(component)

    temp = []
    i = 0

    while(True):
        # coord 길이가 0일 경우 반복문 중단
        if len(coord) == 0:
            break

        # temp 리스트에 coord의 i번째와 i+1번째 항목을 추가
        temp.append(coord[i])
        temp.append(coord[i+1])
        
        # text 변수 = (첫번째항목, 두번째 항목) 형식의 문자열 저장
        text = '({}, {})'.format(temp[0], temp[1])

        # out_img에 text 문자열을 temp 위치에 지정된 폰트로 출력
        out_img = cv2.putText(out_img, text, temp, font, 1, (255,0,0), 1)
        # temp 리스트 비우기
        temp.clear()
        i += 2

        # i의 값이 coord의 길이보다 클 경우 반복문 중단
        if i >= len(coord):
            break

    # out_img에 cv_keypoints 변수에 저장된 키포인트를 이용하여 키포인트 그리기 (색상도 지정, 플래그 사용)  
    # cv2.DRAW... = 키포인트에 있는 사이즈나 앵글에 들어있는 변수를 고려하여 다양한 크기와 직선을 이용해서 표현
    out_img = cv2.drawKeypoints(
        out_img, cv_keypoints, outImage=np.array([]), color=(255, 255, 0),
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
      
    # cv2.polylines 함수를 이용하여 스켈레톤 그리기 (이미지, 다각형 좌표, 다각형 닫힘 여부, 색상 전달)  
    out_img = cv2.polylines(out_img, adjacent_keypoints, isClosed=False, color=(255, 255, 0))

    # 반환값은 스켈레톤이 그려진 이미지 반환
    return out_img
