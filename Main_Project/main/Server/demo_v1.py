"""
author : 김민관
date : 2023/03/17
detail : 서버에서 동작할 프로그램
"""
# >> pseudo code << 
# procedure of main() function in server
#
# 서버를 실행, cap을 받아와야됨
# img = server.server()
# posenet 실행
# posent_flag, trigger_y, hand_y = posenet.detection(img, trigger)
# posenet 실행중 특이 사항 발생 확인
# detection() 에서 posenet_flag와 어깨의 y좌표, 올라간 손의좌표를 받아옴
# if posenet_flag == True
#
# 제스처 트리거 함수 실행
# trigger = hand.gesture_trigger(img, posenet_flag, 손의 좌표)
# getsture_trigger에서는 손가락의 모션을 찍기위해 손의 좌표주변만 input함
#
# 트리거 동작 확인
# if trigger == True
# 제스처 모드 시작
# posenet.detection(img, trigger)
# 이런 저런 제스처를 확인하고 돌아옴
#
# 통신이 끊어지 않는한 무한 반복
#
# end of procedure

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import server
import posenet
import hand
import cv2


def main():
    with tf.Session() as sess:
        trigger = False #손이 머리위로 올라간 상태를 확인하는 플래
        inital = False # hand_gesture 초기화 플래그
        gesture = False # 행동의 제스처 판단 함수를 실행할지 결정하는 파라미터
        model_cfg, model_outputs = posenet.load_model(posenet.MODEL, sess)
        hands_data, count, now_dist = hand.hand_gesture()

        conn, addr = server.server_init()
        command = 'hello'

        while True:
            # frame 받아오기
            frame = server.get_stream(conn)

                # 원래 webcam_demo의 메인 반복문
                #posnet_flag, trigger_y, hand_y = posenet.detection(img, model_cfg, model_outputs, sess, trigger)
            img_overlay, trigger, command = posenet.detection(
                frame, model_cfg, model_outputs, sess, gesture, command
                )

            # 모션 제어로 넘어가려는게 확인되면 trigger를 종료해서 다시 포즈넷 가동
            if gesture is True:
                trigger = False

            if trigger is True:
                # mediapip hand 실행전 초기화
                img_overlay, gesture, count, now_dist = hand.check_trigger(
                    frame, hands_data, count, now_dist
                    )

            if trigger is False and gesture is False:
                command = 0

            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    command = 'NOT'

            # send가 없으면 client측이 정지함       
            server.send(conn, command)
            
            # 모션 제어를 종료하라는 신호가 오면 파라미터 초기화
            if command is 8:
                command = 0
                gesture = False


            # 1. 포즈넷에서 코와 손목의 좌표를 받아오는 모드
            # 2. 손이 머리 위로 올라갔을 때, trigger == True
            # 3. trigger == True 일때는 손의 제스처를 판단해야함
            #    3-1. 손의 제스처를 판단하는 도중에 손이 머리 아래로 내려온다면?
            #    3-2. trigger == False로 바꿔서 1.로 돌아감

            # 4. 손의 제스처가 인정되면, gesture == True 로 바꿔야함
            #    4-1. gesture == True라면 trigger == False가 되어야함

            # 5. gesture == True 라면 포즈넷에 모드를 모션 인식 모드로 바꿔야함
            #    5-1. 모션 인신 모드 중에 손이 아래로 내려온다면?
            #    5-2. gesture == False로 바꿔서 1.으로 돌아감

            # 6. 모든 상황에서 command는 값이 존재하나, 0과 8번 이 아닐때만 전송함
            # 7. command가 8번이라면 1.으로 돌아가야함
            

            cv2.imshow('test', img_overlay)
            if cv2.waitKey(5) & 0xFF == 27:
                break


if __name__ == "__main__":
    main()