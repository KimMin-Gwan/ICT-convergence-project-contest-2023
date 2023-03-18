# -*- coding: utf8 -*-
import cv2
import socket
import numpy as np
import server


#서버 연결
def client_sock():
    ## TCP 사용
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ## server에 연결 ip, port
    sock.connect((server.IP, server.PORT))

    return sock

#webcam 기본 설정
def set_cam():
    ## webcam 이미지 capture
    cam = cv2.VideoCapture(0)          #webcam 사용
    #cam = cv2.VideoCapture("test.mp4")  #테스트용 mp4 사용
    
    ## 이미지 속성 변경 3 = width, 4 = height
    cam.set(3, 320)
    cam.set(4, 240)
    
    ## 0~100에서 90의 이미지 품질로 설정 (default = 95)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    return cam, encode_param

#서버로 데이터(웹캡) 보내기
def send(sock, cam, encode_param):
    # 비디오의 한 프레임씩 읽는다.
    # 제대로 읽으면 ret = True, 실패면 ret = False, frame에는 읽은 프레임
    ret, frame = cam.read()
    # cv2. imencode(ext, img [, params])
    # encode_param의 형식으로 frame을 jpg로 이미지를 인코딩한다.
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    # frame을 String 형태로 변환
    data = np.array(frame)
    stringData = data.tostring()
    
    #서버에 데이터 전송
    #(str(len(stringData))).encode().ljust(16)
    sock.sendall((str(len(stringData))).encode().ljust(16) + stringData)

    #cam.release(repr(data.decode()))

    #서버에서 데이터 받아오기
def get(sock):
    #데이터 받아오기 (버퍼 사이즈 1024)
    recv_data = sock.recv(1024)
    #받아온 데이터를 decode하여 data에 저장
    data = recv_data.decode()
    #확인용 출력
    print(data)

    return data
    