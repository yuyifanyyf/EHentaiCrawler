import threading
import time

rotations = ['-', '\\', '|', '/']


class RotationThread(threading.Thread):
    def __init__(self, name, sentence):
        super(RotationThread, self).__init__()  # 调用父类的构造函数
        self.name = name
        self.sentence = sentence
        self.end = False

    def run(self):
        i = 0
        while not self.end:
            i %= 4
            print("\r" + self.sentence + rotations[i], end="")
            i += 1
            time.sleep(0.2)
        print("\r" + self.sentence + "   ")

    def stop(self):
        self.end = True
        time.sleep(0.4)
