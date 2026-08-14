class Robot:
    def __init__(self, id):
        self.id = id
    def work(self):
        print(f"機器人 {self.id} 開始工作")

# 清單裡面裝了三個「匿名物件」
factory_robots = [Robot(1), Robot(2), Robot(3)]

# 透過迴圈統一操作
for robot in factory_robots:
    robot.work()
