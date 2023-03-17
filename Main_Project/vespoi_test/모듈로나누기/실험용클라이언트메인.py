
# server.argument()



#

# 커멘드가 0번인지 확인
# if command is Not 0:
# continue
#
# 아니면 커멘드 실행
# else:
# utils.operater(command)
# 상태에 따라 led켜기

import client
import cv2

def main():
    # 서버 초기값 설정
    sock = client.client_sock('192.168.0.13',5335) #사용시 IP 변경 필요
    cam, encode_param = client.set_cam()


    # 본문 반복문 시작
    # while True:
    while True:
        # 서버로 데이터 전송
        # sever.send()
        client.send(sock, cam, encode_param)
        
        # 커멘드 수신
        # command = sever.get()
        command = client.get(sock) #get 안에 print 있으니 출력 끄려면 확인바람
        # 커멘드가 0번인지 확인
        if command is not 0:
            continue


if __name__ == "__main__":
    main()
