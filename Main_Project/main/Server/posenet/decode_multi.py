from posenet.decode import *
from posenet.constants import *
import time
import scipy.ndimage as ndi

# score가 무엇을 뜻하는걸까.....?
# score는 사람을 구분하는 파라미터로, 사람인게 확인되면 score에 인덱스 별로 기록된다

# 위의 함수와 비슷한 기능을 수행 (입력으로 들어가는 리스트가 다름)
def within_nms_radius_fast(pose_coords, squared_nms_radius, point):

    # pose_coords 배열은 모든 키포인트의 좌표값을 담고있음 (각 행은 하나의 키포인트)
    if not pose_coords.shape[0]:
        return False
    return np.any(np.sum((pose_coords - point) ** 2, axis=1) <= squared_nms_radius)


# 위의 함수와 비슷한 기능을 수행 (입력으로 들어가는 배열이 다름)
def get_instance_score_fast(
        exist_pose_coords,
        squared_nms_radius,
        keypoint_scores, keypoint_coords):

    # 배열이 비어있는지 확인 후 비어있지 않다면 exist..배열의 모든 행과 keypoint... 배열의 모든 행 간의 거리 계산
    if exist_pose_coords.shape[0]:
        s = np.sum((exist_pose_coords - keypoint_coords) ** 2, axis=2) > squared_nms_radius
        not_overlapped_scores = np.sum(keypoint_scores[np.all(s, axis=0)])

    # 배열이 비어있다면 keypoint_scores 배열의 모든 값을 더하기    
    else:
        not_overlapped_scores = np.sum(keypoint_scores)

    # 반환값은 현재 프레임에서 찾은 포즈의 score를 의미 ?    
    return not_overlapped_scores / len(keypoint_scores)


# 위의 함수와 비슷한 기능을 수행 ? (함수를 호출여부 차이인듯?)
def build_part_with_score_fast(score_threshold, local_max_radius, scores):
    parts = []
    num_keypoints = scores.shape[2]
    lmd = 2 * local_max_radius + 1

    # 특정 위치에서 최대값을 가진 위치를 찾아서 parts 리스트에 추가 
    for keypoint_id in range(num_keypoints):
        kp_scores = scores[:, :, keypoint_id].copy()
        kp_scores[kp_scores < score_threshold] = 0  

        max_vals = ndi.maximum_filter(kp_scores, size=lmd, mode='constant')
        max_loc = np.logical_and(kp_scores == max_vals, kp_scores > 0)

        max_loc_idx = max_loc.nonzero()
        for y, x in zip(*max_loc_idx):
            parts.append((
                scores[y, x, keypoint_id],
                keypoint_id,
                np.array((y, x))
            ))
    #print(parts)

    return parts

# 여러 인물들의 포즈를 디코딩하는 함수
def decode_multiple_poses(
        scores, offsets, displacements_fwd, displacements_bwd, output_stride,
        max_pose_detections=10, score_threshold=0.5, nms_radius=20, min_pose_score=0.5):

    pose_count = 0
    # 각 인스턴스의 점수를 저장하는 배열
    pose_scores = np.zeros(max_pose_detections)
    # 각 인스턴스의 모든 키포인트의 점수를 저장하는 배열 (2차원)
    pose_keypoint_scores = np.zeros((max_pose_detections, NUM_KEYPOINTS))
    # 각 인스턴스의 모든 키포인트의 좌표를 저장하는 배열 (3차원)
    pose_keypoint_coords = np.zeros((max_pose_detections, NUM_KEYPOINTS, 2))

    squared_nms_radius = nms_radius ** 2

    # 함수를 통해 반환된값을 score_parts에 저장하고 점수가 높은 순서대로 정렬하기
    scored_parts = build_part_with_score_fast(score_threshold, LOCAL_MAXIMUM_RADIUS, scores)
    scored_parts = sorted(scored_parts, key=lambda x: x[0], reverse=True)
    height = scores.shape[0]
    width = scores.shape[1]
    # 각 배열을 재구성하고 마지막 두 축을 바꾸어 배열을 갱신
    offsets = offsets.reshape(height, width, 2, -1).swapaxes(2, 3)
    displacements_fwd = displacements_fwd.reshape(height, width, 2, -1).swapaxes(2, 3)
    displacements_bwd = displacements_bwd.reshape(height, width, 2, -1).swapaxes(2, 3)

    
    for root_score, root_id, root_coord in scored_parts:

        # 각 값을 이용하여 root_point의 이미지 좌표를 계산
        root_image_coords = root_coord * output_stride + offsets[
            root_coord[0], root_coord[1], root_id]

        # 현재 예측된 포즈와 중복되는지 확인
        if within_nms_radius_fast(
                pose_keypoint_coords[:pose_count, root_id, :], squared_nms_radius, root_image_coords):
            continue

        # 중복되지않는다면 decode_pose함수를 통해 root와 연결된 모든 부위의 포즈 정보를 계산    
        keypoint_scores, keypoint_coords = decode_pose(
            root_score, root_id, root_image_coords,
            scores, offsets, output_stride,
            displacements_fwd, displacements_bwd)

        # get_instance...함수를 통해 인스턴스에 대한 점수 계산
        pose_score = get_instance_score_fast(
            pose_keypoint_coords[:pose_count, :, :], squared_nms_radius, keypoint_scores, keypoint_coords)

        # 이 과정들을 반복하여 프레임에 있는 모든 포즈에 대한 정보를 담기

        # 감지된 포즈들에 대한 결과를 저장하는 과정
        # 조건 만족 여부에 따른 반복문 루프 종료 여부 결정
        if min_pose_score == 0. or pose_score >= min_pose_score:
            pose_scores[pose_count] = pose_score
            pose_keypoint_scores[pose_count, :] = keypoint_scores
            pose_keypoint_coords[pose_count, :, :] = keypoint_coords
            pose_count += 1

        if pose_count >= max_pose_detections:
            break

    # 감지된 포즈의 개수, 포즈 점수, 포즈의 키포인트 좌표를 담고 있는 numpy 배열         
    return pose_scores, pose_keypoint_scores, pose_keypoint_coords
