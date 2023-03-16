# -*- coding: utf8 -*-
import cv2
import socket
import numpy as np
 
## UDP 사용
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
## server ip, port
ip='192.168.0.13'
#ip='127.0.0.1'
#ip='222.103.25.65'
port = 5335

 
while True:
    # 서버로 데이터 전송
    message = "test"
    client_sock.sendto(message.encode(), (ip, port))

    #서버에서 데이터 받아오기 테스트
    data, addr = client_sock.recvfrom(1024)
    print(data.decode())
 
