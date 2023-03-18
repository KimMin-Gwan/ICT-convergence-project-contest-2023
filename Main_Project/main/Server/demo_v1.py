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
        conn, addr = server.server_init()
        command = 0

        while True:
            # frame 받아오기
            frame = server.get_stream(conn)
            
            if trigger is False:
                # 원래 webcam_demo의 메인 반복문
                #posnet_flag, trigger_y, hand_y = posenet.detection(img, model_cfg, model_outputs, sess, trigger)
                img_overlay, trigger, command = posenet.detection(
                    frame, model_cfg, model_outputs, sess, gesture, command
                    )
            else:
                # mediapip hand 실행전 초기화
                if inital is False:
                    hands, count, inital = hand.hand_gesture(inital)
                img_overlay, gesture, count = hand.check_trigger(img_overlay, hands, count)
            
            # 모션 제어로 넘어가려는게 확인되면 trigger를 종료해서 다시 포즈넷 가동
            if gesture is True:
                trigger = False
            
            # command가 존재하고, 8 : done 이 아닐때 
            if command is not 0 and command is not 8:
                server.send(conn, 'hello')
                print('gesture detected')
            
            # 모션 제어를 종료하라는 신호가 오면 파라미터 초기화
            if command is 8:
                command = 0
                gesture = False

            if command is 1:
                command = 0
                gesture = False

            cv2.imshow('test', img_overlay)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    main()