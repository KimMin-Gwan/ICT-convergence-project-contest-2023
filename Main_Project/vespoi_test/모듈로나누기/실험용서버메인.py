import server
import cv2

def main():
    conn, addr = server.server() 

    #실험용 임시 데이터
    command = "test"

    while True:
        # frame 받아오기
        frame = server.get_stream(conn)
        cv2.imshow('ImageWindow',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # command가 존재하고, 8 : done 이 아닐때
        # command 타입int 사용시 TypeError발생(bytes-like object is required)
        if command is not 0 and command is not 8:
            server.send(conn, command)


if __name__ == "__main__":
    main()