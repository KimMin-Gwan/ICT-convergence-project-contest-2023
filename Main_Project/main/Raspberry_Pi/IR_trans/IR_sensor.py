import os
import IR_trans

#tv전원 on/off 기능
def tv_power():
    os.system(IR_trans.power)   #신호를 한 번 보낼 때 여러번 보냄 

#채널업
def tv_channelup():
    os.system(IR_trans.ch_up)

#채널 다운
def tv_channeldown():
    os.system(IR_trans.ch_down)

#소리 줄임
def tv_volumedown():
    os.system(IR_trans.vol_down)

#소리 키움
def tv_volumeup():
    os.system(IR_trans.vol_up)