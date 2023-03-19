import cv2
import posenet

# 본문에 있던 while 돌아가는 부분
def detection(frame, model_cfg, model_outputs, sess, gesture, command, parts):
    input_image, display_image, output_scale = posenet.read_cap(
        frame, scale_factor=posenet.SCALE_FACTOR, output_stride=model_cfg['output_stride'])

    heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
        model_outputs,
        feed_dict={'image:0': input_image}
    )

    pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multi.decode_multiple_poses(
        heatmaps_result.squeeze(axis=0),
        offsets_result.squeeze(axis=0),
        displacement_fwd_result.squeeze(axis=0),
        displacement_bwd_result.squeeze(axis=0),
        output_stride=model_cfg['output_stride'],
        max_pose_detections=10,
        min_pose_score=0.15)

    keypoint_coords *= output_scale

    #overlay_image = posenet.draw_skel_and_kp(
    #    display_image, pose_scores, keypoint_scores, keypoint_coords,
    #    min_pose_score=0.15, min_part_score=0.1)

    if gesture is True:
        overlay_image, command, parts = posenet.figure_out_command(
            display_image, pose_scores, keypoint_scores, keypoint_coords, command, parts)
        '''
        overlay_image, trigger = posenet.draw_part_name(
            display_image, pose_scores, keypoint_scores, keypoint_coords,
            min_pose_score=0.15, min_part_score=0.1)
        command = 1
        '''

    else:
        overlay_image, trigger = posenet.draw_part_name(
            display_image, pose_scores, keypoint_scores, keypoint_coords,
            min_pose_score=0.15, min_part_score=0.1)
    
    
    return overlay_image, trigger, command, parts
