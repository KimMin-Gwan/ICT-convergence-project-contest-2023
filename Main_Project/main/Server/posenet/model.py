import posenet.converter.config

#텐서플로우 버전 1을 사용하도록 
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior() #tensorflow V2의 함수를 비활성화

import os
# 경고 수준을 2단계로 설정(경고 비활성화)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
MODEL_DIR = './_models'


def model_id_to_ord(model_id):
    if 0 <= model_id < 4:
        return model_id  # id is already ordinal
    elif model_id == 50:
        return 0
    elif model_id == 75:
        return 1
    elif model_id == 100:
        return 2
    else:  # 101
        return 3
    

def load_config(model_ord):
    converter_cfg = posenet.converter.config.load_config() #config.yaml 파일을 읽어온다.
    #config.yaml은 mobilenet 에서 사용하는 model의 세부정보가 기록되어있다.

    checkpoints = converter_cfg['checkpoints'] # config.yaml에 기록된 checkpoints 배열을 가지고옴
    #checkpoints: [ 'mobilenet_v1_050', 'mobilenet_v1_075', 'mobilenet_v1_100', 'mobilenet_v1_101'] 

    output_stride = converter_cfg['outputStride'] # config.yaml에 기록된 outputStride
    #outputStride :  16

    checkpoint_name = checkpoints[model_ord] #model_ord = 3
    #checkpoint_name : mobilenet_v1_100

    model_cfg = {
        'output_stride': output_stride, # 16
        'checkpoint_name': checkpoint_name, # mobilenet_v1_101
    }

    return model_cfg



def load_model(model_id, sess, model_dir=MODEL_DIR):
    model_ord = model_id_to_ord(model_id) #if input 101, return 3
    model_cfg = load_config(model_ord)  #리턴되서 받아온 값은 아래와 같다
    """
    model_cfg = {
        'output_stride': output_stride, # 16
        'checkpoint_name': checkpoint_name, # mobilenet_v1_101
    }
    """
    model_path = os.path.join(model_dir, 'model-%s.pb' % model_cfg['checkpoint_name'])
    
    #대충 tfjs2python.py에서 convert함수를 통해 모델을 생성한다는 뜻
    if not os.path.exists(model_path):
        print('Cannot find model file %s, converting from tfjs...' % model_path)
        from posenet.converter.tfjs2python import convert
        convert(model_ord, model_dir, check=False)
        assert os.path.exists(model_path)
    
    # tensorflow 모델을 불러오는 부분
    with tf.gfile.GFile(model_path, 'rb') as f:
        graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    #session에 모델을 올려준다
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name ='')

    offsets = sess.graph.get_tensor_by_name('offset_2:0')
    displacement_fwd = sess.graph.get_tensor_by_name('displacement_fwd_2:0')
    displacement_bwd = sess.graph.get_tensor_by_name('displacement_bwd_2:0')
    heatmaps = sess.graph.get_tensor_by_name('heatmap:0')

    #모델 내용을 리턴 ({모델 이름, 아웃풋 갯수}, 텐서모델명, 텐서 모델 오프셋, 연산이 필요한 데이터, 연산이 끝난 데이터,)
    return model_cfg, [heatmaps, offsets, displacement_fwd, displacement_bwd]










