import server
import IR_sensor
import utils

# 초기값 값 설정
# 서버 초기값 설정
# IR 센서 초기값 설정
server.argument()
IR_sensor.setup()

# 초록색 LED를 켜는 함수(프로그램 동작)
def turn_on_green_LED():
    IR_sensor.turn_on_LED("green")
    IR_sensor.turn_off_LED("red")
    IR_sensor.turn_off_LED("blue")

# 파란색 LED를 켜는 함수(커멘드가 0이 아닐경우)
def turn_on_blue_LED():
    IR_sensor.turn_off_LED("green")
    IR_sensor.turn_off_LED("red")
    IR_sensor.turn_on_LED("blue")

# 빨간색 LED를 켜는 함수 (커멘드가 0일 경우)
def turn_on_red_LED():
    IR_sensor.turn_off_LED("green")
    IR_sensor.turn_on_LED("red")
    IR_sensor.turn_off_LED("blue")

# 기본 상태를 초록색 LED가 켜짐으로써 확인하기
turn_on_green_LED()

# 통신이 끊어지 않는한 무한 반복
while True:
    # 서버로 데이터 전송하기
    server.send()    

    # 커멘드 수신하기
    command = server.get()

    # 커멘드가 0번일 경우
    if command == 0:
        # 빨간색 LED를 켜기
        turn_on_red_LED()

    # 커맨드가 0이 아닐 경우
    else:
        # 파란색 LED를 켜기 
        turn_on_blue_LED()

    # 현재 상태 가져오기
    status = utils.get_status()

    # 상태에 따라 LED 색상 변경하기 
    if status == "on":
        IR_sensor.turn_on_LED()
    elif status == "off":
        turn_on_red_LED()
    
    # 다시 초록색 LED를 켜기 (기본상태라는 뜻)
    turn_on_green_LED()