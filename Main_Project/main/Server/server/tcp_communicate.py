import socket
import cv2
import numpy as np
import server
 
#socket에서 수신한 버퍼를 반환하는 함수
def recvall(sock, count):
    # 바이트 문자열
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf
 
#서버 구동
def server():
    #TCP 사용
    server_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Socket created')
    
    #서버의 아이피와 포트번호 지정
    #s.bind((HOST,PORT))
    server_sock.bind((server.HOST, server.PORT))
    print('Socket bind complete')
    # 클라이언트의 접속을 기다린다. (클라이언트 연결을 10개까지 받는다)
    server_sock.listen(10)
    print('Socket now listening')
    
    #연결, conn에는 소켓 객체, addr은 소켓에 바인드 된 주소
    conn,addr=server_sock.accept()

    return conn,addr
 
#cliet로 부터 웹캠 이미지(영상) 받아오기
def get_stream(conn):
    # client에서 받은 stringData의 크기 (==(str(len(stringData))).encode().ljust(16))
    length = recvall(conn, 16)
    stringData = recvall(conn, int(length))
    data = np.fromstring(stringData, dtype = 'uint8')
    
    #data를 디코딩한다.
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    #cv2.imshow('ImageWindow',frame)
    #cv2.waitKey(1)

    return frame

    #client로 데이터 보내기
def send(conn, command):
    conn.send(command.encode())