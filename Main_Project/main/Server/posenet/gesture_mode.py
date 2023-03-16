import cv2 
import numpy as np  

import posenet.constants

# command 인덱스 
# 0 : nothing, 1 : next, 2 : previous, 3 : up, 4 : down, 5 : shutdown
# 6 : turn on  7 : others 8 : done(제스처 모드를 끄시오)

def figure_out_command(
    display_image, pose_scores, keypoint_scores, keypoint_coords, command,
    min_pose_score=0.15, min_part_score=0.1):
    
    #utils에 있는 draw_part_name 함수를 참고하여 위의 파라미터를 사용할것

    return display_image, command

# 커맨드를 찾는 것을 함수로 만들것(ex. def check_motion():)
# 0일때는 그냥 확인하면됨
# 0이 아닌상태에서는 다음 커맨드를 입력하기 위해 손의 위치가 처음과 유사한 곳으로 왔는지 확인
# 확인 하고 나서 다음 커맨드 찾기
# 만약 손의 위치가 어깨 아래로 내려가면 다 무시하고 command를 8번으로 해서 리턴할것
