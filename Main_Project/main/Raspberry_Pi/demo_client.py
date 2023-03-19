import RPi.GPIO as GPIO
import server
from IR_trans import IR_sensor

# GPIO 모듈 BOARD 모드로 사용
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GREEN_LED = 11 # 초록색 LED 11번 핀에 연결
BLUE_LED = 13 # 파란색 LED 13번 핀에 연결
RED_LED = 15 # 빨간색 LED 15번 핀에 연결

# LED 초기화 
# 초록색은 프로그램을 실행여부를 보이는 것으로 초기상태도 켜져있음.
GPIO.setup(GREEN_LED, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(BLUE_LED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(RED_LED, GPIO.OUT, initial=GPIO.LOW)


def main():

    while True:

        # 서버에서 커멘드의 값 받아오기(문자열 형태)
        command = server.get()

        if command == 'command not detected':
            # 커멘드를 인식하지 못한다는 의미로 빨간색 LED 켜기
            GPIO.output(RED_LED, True)
            # 반복문 중단하기 
            break
            
        # 커멘드의 값이 0이 아닐 경우
        if command != 0:
            # 제스쳐모드가 실행되었다는 의미로 파란색 LED 켜기
            GPIO.output(BLUE_LED, True)

            # 커멘드의 값이 'next'일 경우
            if command == 1:
                # 채널 업 
                IR_sensor.tv_channelup()

            # 커멘드의 값이 'previous'일 경우
            elif command == 2:
                # 채널 다운
                IR_sensor.tv_channeldown()
            
            # 커멘드의 값이 'up'일 경우
            elif command == 3:
                # 볼륨 업
                IR_sensor.tv_volumeup()
            
            # 커멘드의 값이 'down'일 경우
            elif command == 4:
                # 볼륨 다운 
                IR_sensor.tv_volumedown()
            
            # 커멘드의 값이 'turn on'일 경우
            elif command == 6:
                # 전원 on
                IR_sensor.tv_power()
            
            # 커멘드의 값이 'done'일 경우
            elif command == 8:
                # 제스쳐모드를 중단한다는 의미이므로 파란색 LED 끄기
                GPIO.output(BLUE_LED, False)
                break 

        # 커멘드의 값이 0일 경우 (아무 동작 없음)
        else:
            # 다음 반복문 실행하기 
            continue

    # GPIO 리셋    
    GPIO.cleanup()

if __name__ == "__main__":
    main()