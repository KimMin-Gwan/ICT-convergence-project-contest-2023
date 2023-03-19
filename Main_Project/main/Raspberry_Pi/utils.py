from IR_trans import IR_sensor


def handle_command(command):
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