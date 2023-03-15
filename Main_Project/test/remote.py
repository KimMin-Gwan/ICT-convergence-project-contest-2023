import os
import time

for i in range(1,4):
    os.system('irsend SEND_ONCE wow4 KEY_POWER')
time.sleep(20)
os.system('irsend SEND_ONCE wow4 KEY_CHANNELUP')
time.sleep(20)
os.system('irsend SEND_ONCE wow4 KEY_CHANNELDOWN')
time.sleep(20)

for j in range(1,4):
    os.system('irsend SEND_ONCE wow4 KEY_MUTE')