import cv2 
import numpy as np  
import math

def get_dist(x1, x2, y1, y2):
    dist_power = (x2 - x1) ** 2 + (y2 - y1) ** 2
    return math.sqrt(dist_power)

# Parts 객체
class Parts():
    #기본 생성자 
    def __init__(self):
        self.nose = None
        self.l_hand = {'x': 0, 'y': 0}
        self.r_hand = {'x': 0, 'y': 0}
        self.l_eye = {'x': 0, 'y': 0}
        self.r_eye = {'x': 0, 'y': 0}
        self.eye_dist = 0      # 눈 사이 간경(척도)
        self.switch = False     # 함수 종료 조건
        self.init_flag = False  # 초기위치 정했는지 flag
        self.return_flag = False # 초기위치 복귀 확인 flag
        self.initial_position = ['None', {'x': 0, 'y': 0}] # 초기 위치
        self.moved_position = ['None', {'x': 0, 'y': 0}] # 연산 중 임시 기록 위치
        self.other_hand_position = ['None', {'x' : 0, 'y' : 0}] # 기준 반대손
        self.counter = 0  # 변화하는 값 갯수 체크
        self.two_hand = False
        self.diff = np.array([])

    # 처음으로 초기화
    def reset(self):
        self.nose = 0
        self.l_hand = {'x': 0, 'y': 0}
        self.r_hand = {'x': 0, 'y': 0}
        self.l_eye = {'x': 0, 'y': 0}
        self.r_eye = {'x': 0, 'y': 0}
        self.eye_dist = 0      # 눈 사이 간경(척도)
        self.switch = False     # 함수 종료 조건
        self.init_flag = False  # 초기위치 정했는지 flag
        self.return_flag = False # 초기위치 복귀 확인 flag
        self.initial_position = ['None', {'x': 0, 'y': 0}] # 초기 위치
        self.moved_position = ['None', {'x': 0, 'y': 0}] # 연산 중 임시 기록 위치
        self.other_hand_position = ['None', {'x' : 0, 'y' : 0}] # 기준 반대손
        self.counter = 0
        self.two_hand = False
        self.diff = np.array([])

    def return_reset(self):
        self.init_flag = True  # 초기위치 정했는지 flag(init은 안할꺼라 True)
        self.return_flag = True # 초기위치 복귀 확인 : return reset이니까 True
        self.moved_position = ['None', {'x': 0, 'y': 0}] # 연산 중 임시 기록 위치
        self.other_hand_position = ['None', {'x' : 0, 'y' : 0}] # 기준 반대손
        self.counter = 0
        self.diff = np.array([])

    def nose_coord(self, y):
        self.nose = y

    def left_hand_coord(self, x, y):
        self.l_hand['x'] = x
        self.l_hand['y'] = y

    def right_hand_coord(self, x, y):
        self.r_hand['x'] = x
        self.r_hand['y'] = y

    def left_eye_coord(self, x, y):
        self.l_eye['x'] = x
        self.l_eye['y'] = y

    def right_eye_coord(self, x, y):
        self.r_eye['x'] = x
        self.r_eye['y'] = y

    def get_eye_dist(self):
        l_x = self.l_eye['x']
        l_y = self.l_eye['y']
        r_x = self.r_eye['x']
        r_y = self.r_eye['y']

        self.eye_dist = get_dist(l_x, r_x, l_y, r_y)   
        self.ref = self.eye_dist // 6

    # 제스처 모드 종료 확인
    def check_switch(self):
        if self.l_hand['y'] != 0 or self.r_hand['y'] != 0:
            if self.l_hand['y'] < self.nose or self.r_hand['y'] < self.nose:
                self.switch = True
            else:
                self.switch = False
            return self.switch
        return self.switch
    
    #  손의 초기 위치 확인
    def init_positioning(self):
        if self.switch is False:
            self.initial_position[0] = 'None'
            self.initial_position[1] = {'x': 0, 'y': 0}
            self.init_flag = False

        if self.l_hand['y'] > self.nose:
            self.initial_position[0] = 'LEFT'
            self.initial_position[1] = {'x': self.l_hand['x'], 'y': self.l_hand['y']}
            self.init_flag = True
        
        elif self.r_hand['y'] > self.nose:
            self.initial_position[0] = 'RIGHT'
            self.initial_position[1] = {'x': self.r_hand['x'], 'y': self.r_hand['y']}
            self.init_flag = True
        
        else:
            self.initial_position[0] = 'RIGHT'
            self.initial_position[1] = {'x': self.l_hand['x'], 'y': self.l_hand['y']}
            self.init_flag = True

        self.get_eye_dist()

    def check_two_hand(self):
        # True이면 양손 모드, False는 한손 모드
        if self.l_hand['y'] != 0 or self.r_hand['y'] != 0:
            if self.l_hand['y'] < self.nose and self.r_hand['y'] < self.nose:
                self.two_hand = True
                return self.two_hand
            else:
                self.two_hand = False 
                return self.two_hand 
        else:
            return self.two_hand

    # 손의 처음 위치와 현재 위치의 차이를 파악하는 함수
    def check_return(self):
        if self.initial_position[0] is 'LEFT':
            diff = get_dist(
                self.initial_position[1]['x'],
                self.l_hand['x'],
                self.initial_position[1]['y'],
                self.l_hand['y'],
            )
            print('chekc diff : ', diff)
            if diff < self.ref:
                return True
            else:
                return False

        elif self.initial_position[0] is 'RIGHT':
            diff = get_dist(
                self.initial_position[1]['x'],
                self.r_hand['x'],
                self.initial_position[1]['y'],
                self.r_hand['y'],
            )
            print('chekc diff : ', diff)
            if diff < 10:
                return True
            else:
                return False

        else:
            return False

    # 카운터 추가   
    def addCounter(self):
        self.counter += 1

    # 카운터 리셋
    def resetCounter(self):
        self.counter = 0
        self.diff = np.array([])


    # 한손일 때 구분하는 맴버 함수 
    def command_1_2_cal(self, diff):
        if self.initial_position[0] is 'LEFT':
            if diff < 0:
                if abs(diff) >= self.ref:
                    self.moved_position[1]['x'] = self.l_hand['x']
                    self.diff = np.append(self.diff, diff)
                    self.addCounter()

            else :
                if abs(diff) >= self.ref:
                    self.moved_position[1]['x'] = self.l_hand['x']
                    self.diff = np.append(self.diff, diff)
                    self.addCounter()

        if self.initial_position[0] is 'RIGHT':
            if diff < 0:
                if abs(diff) >= self.ref:
                    self.moved_position[1]['x'] = self.r_hand['x']
                    self.diff = np.append(self.diff, diff)
                    self.addCounter()

            else :
                if abs(diff) >= self.ref:
                    self.moved_position[1]['x'] = self.r_hand['x']
                    self.diff = np.append(self.diff, diff)
                    self.addCounter()

    def get_other_hand(self, key):
        if key is 'LEFT':
            self.other_hand_position[0] = "RIGHT"
            self.other_hand_position[1]['x'] = self.r_hand['x']
            self.other_hand_position[1]['y'] = self.r_hand['y']
        elif key is 'RIGHT':
            self.other_hand_position[0] = "LEFT"
            self.other_hand_position[1]['x'] = self.l_hand['x']
            self.other_hand_position[1]['y'] = self.l_hand['y']
        else :
            self.other_hand_position[0] = "NONE"
            self.other_hand_position[1]['x'] = 0
            self.other_hand_position[1]['y'] = 0
    
    def other_hand_check(self):
        if self.other_hand_position[0] is 'LEFT':
            x1 = self.other_hand_position[1]['x']
            x2 = self.l_hand['x']
            #y1 = self.other_hand_position[1]['y']
            #y2 = self.r_hand['y']
            self.dist = x1 - x2
            #self.dist = get_dist(x1, x2, y1, y2)

        elif self.other_hand_position[0] is 'RIGHT':
            x1 = self.other_hand_position[1]['x']
            x2 = self.r_hand['x']
            #y1 = self.other_hand_position[1]['y']
            #y2 = self.l_hand['y']
            self.dist = x1 - x2
            #self.dist = get_dist(x1, x2, y1, y2)

        else :
            self.dist = 0
        

