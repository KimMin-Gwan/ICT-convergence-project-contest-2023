import cv2 
import numpy as np  
import math

import posenet.constants
from posenet.parts import Parts


# 값이 전체적으로 증가하는지 감소하는지 구분하는 함수
def trend(x):
    sumDiff = np.sum(x)

    if sumDiff < 0 :
        return 1
    elif sumDiff > 0 :
        return 2
    else:
        return 7

def get_command_1_2(parts, command):
    # command = 1 (next)
    # 시작 지점 기준으로 손이 오른쪽으로 이동한 프레임이 5개 이상이면 next
    # 시작 지점 : parts.intital_position
    # 기준 : 이전 프레임에 기록된 parts.moved_postition['x']
    # 5번 움직이는걸 측정하는 척도 parts.count
    # 다확인하고 나면 count 초기화 시켜줄것
    print('im in one hand mode')

    #print('Count : ', parts.counter)
    #print('inintal_ pos : ', parts.initial_position[1]['x'] , ' ', parts.initial_position[1]['y'])
    #print('moved pos : ', parts.moved_position[1]['x'] ,' ', parts.moved_position[1]['y'])
    #print('right hand  pos : ', parts.r_hand['x'] , ' ', parts.r_hand['y'])
    


    # 초기값일 때
    if parts.counter == 0:
        #'왼손일 때'
        if parts.initial_position[0] is 'LEFT':
            diff = parts.l_hand['x'] - parts.initial_position[1]['x']
            parts.command_1_2_cal(diff)
        
        #'오른손일 때'
        elif parts.initial_position[0] is 'RIGHT':

            diff = parts.r_hand['x'] - parts.initial_position[1]['x']
            parts.command_1_2_cal(diff)
    
    else:
        if parts.initial_position[0] is 'LEFT':

            diff = parts.l_hand['x'] - parts.moved_position[1]['x']
            parts.command_1_2_cal(diff)

        
        #'오른손일 때'
        elif parts.initial_position[0] is 'RIGHT':
            diff = parts.r_hand['x'] - parts.moved_position[1]['x']
            parts.command_1_2_cal(diff)
    
    if parts.counter > 4:
        command = trend(parts.diff)
        parts.resetCounter()
    
    return command, parts


def get_command_3_4_5_6(parts, command):
    # command 3, 4, 5
    # 일단 기준 손이 있어야함
    # 반대손의 위치도 알아야함
    # 반대손의 위치가 고정되있다면, 기준 손의 값을 고려해야함
    #   기준 손의 값은 위아래로 움직이고 움직이는 값을 실시간으로 체크해야함
    #   체크된 값이움직인 거리가 눈 사이 * k 만큼 움직일 때 마다 3번이나 4번값을 반환해야함
    # 반대손의 위치가 고정되지 않는다면,
    #   반대손이 위아래로 움직이는지, 좌우로 움직이는지 확인해야함
    #   반대손이 좌우로 움직이면, 기준손의 좌표와의 거리를 실시간으로 체크해야함
    #   위아래로 많이 움직이면, 기준손을 변경해야함
    #   거리가 줄어들면 5, 6번을 반환해야함
    print('im in two hand mode')

    # 방향 플래그
    path_flag = 0 # 0 : nothing 1 : 상승, 2 : 하강, 3 : 종료
    if parts.counter == 0:
    
        parts.get_other_hand(parts.initial_position[0])
        
        #반대손이 고정되어있는지는 확인하지 않고
        #기준 손의 값이 변화하는 것을 확인해야함
        if parts.initial_position[0] is 'LEFT':
            diff = parts.initial_position[1]['y'] - parts.l_hand['y'] 
            if diff == parts.initial_position[1]['y']:
                path_flag = 0

            elif diff < 0 :
                path_flag = 2 

            elif diff > 0:
                path_flag = 1 
            
            else:
                path_flag = 0
            

        
        if parts.initial_position[0] is 'RIGHT':
            diff = parts.initial_position[1]['y'] - parts.r_hand['y'] 
            if diff == parts.initial_position[1]['y']:
                path_flag = 0

            elif diff < 0 :
                path_flag = 2 

            elif diff > 0:
                path_flag = 1 

            else:
                path_flag = 0

        parts.addCounter()
        
    else:
    
        # 반대손이 움직이는 지 확인
        parts.other_hand_check()
        
        #반대손이 고정되어 있다면
        if parts.dist < 20:
            #기준 손의 값이 변화하는 것을 확인해야함
            if parts.initial_position[0] is 'LEFT':
                diff = parts.moved_position[1]['y'] - parts.l_hand['y'] 
                if diff == parts.moved_position[1]['y']:
                    path_flag = 0

                elif diff < 0 :
                    path_flag = 2 

                elif diff > 0:
                    path_flag = 1
                
                else:
                    path_flag = 0
            
            if parts.initial_position[0] is 'RIGHT':
                diff = parts.moved_position[1]['y'] - parts.r_hand['y'] 
                if diff == parts.moved_position[1]['y']:
                    path_flag = 0
                    
                elif diff < 0 :
                    path_flag = 2

                elif diff > 0:
                    path_flag = 1
                    
                else:
                    path_flag = 0

        else:
            if parts.initial_position[0] is 'LEFT':
                diff = parts.other_hand_position[1]['x'] - parts.l_hand['x']
                path_flag = 3 

            elif parts.initial_position[0] is 'RIGHT':
                diff = parts.other_hand_position[1]['x'] - parts.r_hand['x']
                path_flag = 3 


    #하강 이라면
    if path_flag is 1: 
        if abs(diff) < parts.eye_dist:
            command = 7
        if abs(diff) >= parts.eye_dist:
            if parts.initial_position[0] is 'LEFT':
                parts.moved_position[1].update(parts.l_hand)
            elif parts.initial_position[0] is 'RIGHT':
                parts.moved_position[1].update(parts.r_hand)
            command = 3

    # 상승 이라면
    elif path_flag is 2: 
        if abs(diff) < parts.eye_dist:
            command = 7
        elif abs(diff) >= parts.eye_dist:
            if parts.initial_position[0] is 'LEFT':
                parts.moved_position[1].update(parts.l_hand)
            elif parts.initial_position[0] is 'RIGHT':
                parts.moved_position[1].update(parts.r_hand)
            command = 4

    # 이외에는 대기

    elif path_flag is 3:
        command = 5
        

    else:
        command = 0

    return command, parts



# command 인덱스 
# 0 : nothing, 1 : next(1), 2 : previous(1), 3 : up(2), 4 : down(2), 5 : shutdown(2)
# 6 : turn on(2)  7 : others(0) 8 : done(제스처 모드를 끄시오)
    
def get_command(parts, command):
    # 이전에 두손 모드인지 한손모드인지 확인
    # 모드 전환이 발생하면 내부 카운트 초기화
    # 아니라면 그냥 쓰던 함수 호
    
    if parts.two_hand is False:
        if parts.check_two_hand() is False:
            command, parts = get_command_1_2(parts, command)
        else:
            parts.resetCounter()
            command, parts = get_command_3_4_5_6(parts, command)
    else:
        print('else two_hand flag', parts.two_hand)
        if parts.check_two_hand() is False:
            parts.resetCounter()
            command, parts = get_command_1_2(parts, command)
        else:
            command, parts = get_command_3_4_5_6(parts, command)

    return command, parts




# 부위의 좌표를 받아서 객체를 구성하는 함수
def get_parts(
        img, instance_scores, keypoint_scores, keypoint_coords, parts,
        min_pose_score = 0.5, min_part_score=0.5):
    out_img = img
    font = cv2.FONT_HERSHEY_SIMPLEX
    real_co = []
    #부위별 x좌표와 y좌표
    
    for ii, score in enumerate(instance_scores):

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
                        parts.nose_coord(y)

                    elif name == posenet.PART_NAMES[9]:
                        parts.left_hand_coord(x, y)

                    elif name == posenet.PART_NAMES[10]:
                        parts.right_hand_coord(x, y)

                    elif name == posenet.PART_NAMES[1]:
                        parts.left_eye_coord(x, y)

                    elif name == posenet.PART_NAMES[2]:
                        parts.right_eye_coord(x, y)
                            
                # 배열 비우기
                real_co.clear()

    return parts




# command 인덱스 
# 0 : nothing, 1 : next(1), 2 : previous(1), 3 : up(2), 4 : down(2), 5 : shutdown(2)
# 6 : turn on(2)  7 : others(0) 8 : done(제스처 모드를 끄시오)

def figure_out_command(
    display_image, pose_scores, keypoint_scores, keypoint_coords, command, parts):

    # 팔의 좌표를 갱신
    parts = get_parts(
        display_image, pose_scores, keypoint_scores, keypoint_coords, parts,
        min_pose_score = 0.5, min_part_score=0.5)

    # 팔이 내려갔는지 확인함 (팔이 내려가면 다 무시하고 종료)
    flag = parts.check_switch()
    if flag is False:
        print('arm downed ')
        parts.reset()
        command = 8
        return display_image, command, parts

    
    print('right hand  pos : ', parts.r_hand['x'] , ' ', parts.r_hand['y'])

    #  초기 위치 지정이 안되있다면 초기값 지정
    if parts.init_flag is False:
        parts.init_positioning()

    # 1회이상 command가 실행되고나면 손이 제자리로 돌아왔는지 확인
    # 제자리에 돌아왔다면 다음 커멘드를 실행하면 되고,
    # 제자리에 돌아오지 않았다면 손을 내릴 때 까지 other로 반환 (대기)
    # 3, 4번은 연속 동작이므로 리턴 동작이 필요없음
    # 단 3, 4번 커멘드가 끝날 때 7번으로 변경해줘야함
    if command is not 0 and command is not 3 and command is not 4:
        #투 핸드 모드이면 7을 리턴하지 않고 계속 작동
        
        if parts.check_return() is False and parts.two_hand is False: #여기 'and parts.two_hand is False' 추가함 (원핸드 모드일때)
            command = 7
            return display_image, command, parts

        print('next loop')
        parts.return_reset()

        command = 0
    
    # 투핸드 모드에서 한번 보내고나면 다시 초기화 시키는 함수
    if command is 3 or command is 4:
        command = 7

    # 커멘드를 받아오는 부분
    command, parts = get_command(parts, command)

    return display_image, command, parts

