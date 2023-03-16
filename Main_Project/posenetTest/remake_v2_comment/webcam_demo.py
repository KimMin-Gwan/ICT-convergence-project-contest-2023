#import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import cv2
import time
import argparse
import socket
import numpy as np

import posenet
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=int, default=101)
parser.add_argument('--cam_id', type=int, default=0)
parser.add_argument('--cam_width', type=int, default=1280)
parser.add_argument('--cam_height', type=int, default=720)
parser.add_argument('--scale_factor', type=float, default=0.7) #0.7125
parser.add_argument('--file', type=str, default=None, help="Optionally use a video file instead of a live camera")
args = parser.parse_args()


 
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


def main():
    with tf.Session() as sess:

        model_cfg, model_outputs = posenet.load_model(args.model, sess)
        output_stride = model_cfg['output_stride']
        # #HOST = socket.gethostbyname('bd4a-125-185-34-18.jp.ngrok.io') #이건 http라서 안됨 ㅇㅇ
        # #HOST='192.168.0.13'
        # #HOST= '127.0.0.1"
        # PORT=5335
        
        # #TCP 사용
        # s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # print('Socket created')
        
        # #서버의 아이피와 포트번호 지정
        # #s.bind((HOST,PORT))
        # s.bind(( socket.gethostname(),PORT))
        # print('Socket bind complete')
        # # 클라이언트의 접속을 기다린다. (클라이언트 연결을 1개까지 받는다)

        # s.listen(1)
        # print('Socket now listening')
        # conn,addr=s.accept()

        frame = cv2.VideoCapture(0)
        frame.set(3, args.cam_width)
        frame.set(4, args.cam_height)

        start = time.time()
        frame_count = 0
        
        # font=cv2.FONT_HERSHEY_SIMPLEX

        while True:

            # length = recvall(conn, 16)
            # stringData = recvall(conn, int(length))
            # data = np.fromstring(stringData, dtype = 'uint8')
            
            # #data를 디코딩한다.
            # frame = cv2.imdecode(data, cv2.IMREAD_COLOR)

            input_image, display_image, output_scale = posenet.read_cap(
                frame, scale_factor=args.scale_factor, output_stride=output_stride)

            #input_image, display_image, output_scale = posenet.read_cap(
            #    cap, scale_factor=args.scale_factor, output_stride=output_stride)

            heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
                model_outputs,
                feed_dict={'image:0': input_image}
            )
            #print(heatmaps_result)

            pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multi.decode_multiple_poses(
                heatmaps_result.squeeze(axis=0),
                offsets_result.squeeze(axis=0),
                displacement_fwd_result.squeeze(axis=0),
                displacement_bwd_result.squeeze(axis=0),
                output_stride=output_stride,
                max_pose_detections=10,
                min_pose_score=0.15)

            keypoint_coords *= output_scale



            # TODO this isn't particularly fast, use GL for drawing and display someday...
            #overlay_image = posenet.draw_skel_and_kp(
            #    display_image, pose_scores, keypoint_scores, keypoint_coords,
            #    min_pose_score=0.15, min_part_score=0.1)

            overlay_image = posenet.draw_part_name(
                display_image, pose_scores, keypoint_scores, keypoint_coords,
                min_pose_score=0.15, min_part_score=0.1)

            cv2.imshow('posenet', overlay_image)
            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print('Average FPS: ', frame_count / (time.time() - start))

if __name__ == "__main__":
    main()