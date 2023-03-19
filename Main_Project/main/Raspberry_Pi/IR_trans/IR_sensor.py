import os

#tv전원 on/off 기능
def tv_power():
    os.system('irsend -3 # SEND_ONCE wow4 KEY_POWER')   #신호를 한 번 보낼 때 여러번 보냄 

#채널업
def tv_channelup():
    os.system('irsend SEND_ONCE wow4 KEY_CHANNELUP')

#채널 다운
def tv_channeldown():
    os.system('irsend SEND_ONCE wow4 KEY_CHANNELDOWN')

#소리 줄임
def tv_volumedown():
    os.system('irsend SEND_ONCE wow4 KEY_VOLUMEDOWN')

#소리 키움
def tv_volumeup():
    os.system('irsend SEND_ONCE wow4 KEY_VOLUMEUP')