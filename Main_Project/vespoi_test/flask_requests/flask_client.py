

import cv2
import numpy as np
import requests

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 카메라 연결
cap = cv2.VideoCapture('test.mp4')

while True:
    # 카메라에서 프레임 읽기
    ret, frame = cap.read()

    # 프레임 크기 조정
    frame = cv2.resize(frame, (640, 480))

    # JPEG 인코딩
    _, img_encoded = cv2.imencode('.jpg', frame)

    # HTTPS POST 요청 전송
    response = requests.post('https://633c-125-185-34-18.jp.ngrok.io', files={'file': ('image.jpg', img_encoded.tostring(), 'image/jpeg')}, verify=False)
    print(response.content)

    # 'q' 키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료
cap.release()
cv2.destroyAllWindows()
