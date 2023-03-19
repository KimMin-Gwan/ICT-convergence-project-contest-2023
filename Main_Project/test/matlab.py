import random

a = 1
b = 10
prev = 0

for i in range(100):
    current = random.uniform(a, b)
    print(current)
    diff = current - prev
    if diff >= 0:
        print("전체적으로 증가하는 구간이 있습니다.")
        break
    prev = current
else:
    print("전체적으로 감소하는 값입니다.")