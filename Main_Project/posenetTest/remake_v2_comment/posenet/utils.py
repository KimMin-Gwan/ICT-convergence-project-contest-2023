import cv2
import numpy as np
import posenet.constants
import time


def valid_resolution(width, height, output_stride=16):
    target_width = (int(width) // output_stride) * output_stride + 1
    target_height = (int(height) // output_stride) * output_stride + 1

    return target_width, target_height


def _process_input(source_img, scale_factor=1.0, output_stride=16):


    target_width, target_height = valid_resolution(
        source_img.shape[1] * scale_factor, source_img.shape[0] * scale_factor, output_stride=output_stride)
    scale = np.array([source_img.shape[0] / target_height, source_img.shape[1] / target_width])
    #print('target_width = ', target_width)
    #print('target_height = ', target_height)
    
    input_img = cv2.resize(source_img, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
    input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB).astype(np.float32)
    #0.00784
    input_img = input_img * (2.0 / 255.0) - 1.0
    #cv2.imshow('utils', input_img)
    input_img = input_img.reshape(1, target_height, target_width, 3)
    #print(input_img)

    return input_img, source_img, scale


def read_cap(cap, scale_factor=1.0, output_stride=16):
    res, img = cap.read()
    
    if not res:
      raise IOError("webcam failure")

    #return _process_input(cap, scale_factor, output_stride)
    return _process_input(img, scale_factor, output_stride)


def read_imgfile(path, scale_factor=1.0, output_stride=16):
    img = cv2.imread(path)
    return _process_input(img, scale_factor, output_stride)


def draw_keypoints(
        img, instance_scores, keypoint_scores, keypoint_coords,
        min_pose_confidence=0.5, min_part_confidence=0.5):
    cv_keypoints = []
    for ii, score in enumerate(instance_scores):
        if score < min_pose_confidence:
            continue
        for ks, kc in zip(keypoint_scores[ii, :], keypoint_coords[ii, :, :]):
            if ks < min_part_confidence:
                continue
            cv_keypoints.append(cv2.KeyPoint(kc[1], kc[0], 10. * ks))
    out_img = cv2.drawKeypoints(img, cv_keypoints, outImage=np.array([]))
    return out_img

#점의 좌표를 가지고 오는 함수
def get_adjacent_keypoints(keypoint_scores, keypoint_coords, min_confidence=0.1):
    results = [] #리턴시킬 배열 (x, y)
    #posenet에서 받아온 인덱스들의 좌 우를 찍음
    for left, right in posenet.CONNECTED_PART_INDICES:
        if keypoint_scores[left] < min_confidence or keypoint_scores[right] < min_confidence:
            continue
        #받아온 결과를 numpy.array 형식으로 [x, y] 와 같이 저장
        results.append(
            np.array([keypoint_coords[left][::-1], keypoint_coords[right][::-1]]).astype(np.int32),
        )
        #좌표값을 리턴
        #print(results)
    return results


def draw_skeleton(
        img, instance_scores, keypoint_scores, keypoint_coords,
        min_pose_confidence=0.5, min_part_confidence=0.5):
    out_img = img
    adjacent_keypoints = []
    for ii, score in enumerate(instance_scores):
        if score < min_pose_confidence:
            continue
        new_keypoints = get_adjacent_keypoints(
            keypoint_scores[ii, :], keypoint_coords[ii, :, :], min_part_confidence)
        adjacent_keypoints.extend(new_keypoints)
    out_img = cv2.polylines(out_img, adjacent_keypoints, isClosed=False, color=(255, 255, 0))
    return out_img

# 부위를 화면에 표시해주는 함수
def draw_part_name(
        img, instance_scores, keypoint_scores, keypoint_coords,
        min_pose_score = 0.5, min_part_score=0.5):
    out_img = img
    font = cv2.FONT_HERSHEY_SIMPLEX
    real_co = []
    leftWrist_x = 0
    leftWrist_y = 0
    rightWrist_x = 0
    rightWrist_y = 0
    nose_x = 0
    nose_y = 0
    rightElbow_x = 0
    rightElbow_y = 0
    leftElbow_x = 0
    leftElbow_y = 0
    
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
                    # 화면에 잡힌 손과 코의 x,y좌표를 저장
                    #constants.py에 있는 모듈이름 가져오기
                    if name == posenet.PART_NAMES[0]:
                        nose_y = y
                        nose_x = x
                    elif name == posenet.PART_NAMES[9]:
                        leftWrist_x = x
                        leftWrist_y = y
                    elif name == posenet.PART_NAMES[10]:
                        leftWrist_x = x
                        rightWrist_y = y
                    elif name == posenet.PART_NAMES[7]:
                        leftElbow_x = x
                        leftElbow_y = y
                    elif name == posenet.PART_NAMES[8]:
                        leftElbow_x = x
                        rightElbow_y = y
                # 배열 비우기
                real_co.clear()
    # 만약 왼손과 오른손이 화면에 잡히고
    if leftWrist_y and rightWrist_y != 0:
        # 부위중 인식이 안되는 부위가 있다면(좌표가 0이 된다면) 계속 실행되는 버그 수정
        
        #print(nose_x)
        #print(nose_y)
        
        #소리 증가
        if rightWrist_y < nose_y: #오른손이 손 위에 있다면
            print('소리 빠름 증가') #소리는 느리게 증가
            time.sleep(0.2)
        if leftWrist_y < nose_y: #왼손이 코 위로 올리면
            print('소리 느림 증가') #소리는 느리게 증가
            time.sleep(0.8)


        #소리 감소
        if rightWrist_y > rightElbow_y and rightElbow_y != 0: #오른손이 팔꿈치 밑으로 내리면 
            print('소리 빠름 감소') #소리 빠르게 감소
            time.sleep(0.2)
        if leftWrist_y > leftElbow_y and leftElbow_y != 0: #왼손이 팔꿈치 밑으로 내리면 
            print('소리 느림 감소') #소리 느리게 감소
            time.sleep(0.8)

        #채널 이동 (추가예정)
        """
        if rightWrist_x < nose_x:
            print(rightWrist_x)
            print(nose_x)
            print("채널 증가")
            time.sleep(0.5)
        """

    return out_img








def draw_skel_and_kp(
        img, instance_scores, keypoint_scores, keypoint_coords,
        min_pose_score=0.5, min_part_score=0.5):
    out_img = img
    font=cv2.FONT_HERSHEY_SIMPLEX
    adjacent_keypoints = []
    cv_keypoints = []

    part_flag = []

    component = []
    coord = []

    for ii, score in enumerate(instance_scores):
        if score < min_pose_score:
            #part_flag[ii] = 0
            continue


        new_keypoints = get_adjacent_keypoints(
            keypoint_scores[ii, :], keypoint_coords[ii, :, :], min_part_score
        )
        adjacent_keypoints.extend(new_keypoints)


        for ks, kc in zip(keypoint_scores[ii, :], keypoint_coords[ii, :, :]):

            if ks < min_part_score:
                continue

            x = kc[1].astype(np.int32)
            y = kc[0].astype(np.int32)
            component.append(x)
            component.append(y)

            #coord_x = np.append(kc[1].astype(np.int32))
            #coord_y = np.append(kc[0].astype(np.int32))
            cv_keypoints.append(cv2.KeyPoint(kc[1], kc[0], 10. * ks))

        coord.extend(component)

    


    #print(coord)
    temp = []
    i = 0

    while(True):
        if len(coord) == 0:
            break

        temp.append(coord[i])
        temp.append(coord[i+1])


        text = '({}, {})'.format(temp[0], temp[1])
        out_img = cv2.putText(out_img, text, temp, font, 1, (255,0,0), 1)
        temp.clear()
        i += 2

        if i >= len(coord):
            break
        
        


  
    out_img = cv2.drawKeypoints(
        out_img, cv_keypoints, outImage=np.array([]), color=(255, 255, 0),
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )

    #out_img = cv2.polylines(img,       pts,                  isClosed,    color)
    out_img = cv2.polylines(out_img, adjacent_keypoints, isClosed=False, color=(255, 255, 0))
    """
    #temp에 나온 좌표들은 집어 넣는 부분
    temp = []
    for arg in coord:
        for args in arg:
            temp.extend(args)
        #print(temp)
    """


    return out_img
