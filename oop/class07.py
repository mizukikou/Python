 
class Animal:  # 定義父類別
    def fly(self):
        print("時速 20公里!")
 
class Bird(Animal):  # 定義子類別
    def fly(self, speed):  # 覆寫父類別方法
        print("時速 " + str(speed) + "公里!")
 
class Plane:  # 定義類別
    def fly(self):  # 方法1
        print("時速 1000 公里!")
 
    def fly_mile(self, speed):
        print("時速 " + str(speed) + "英哩!")
 
animal = Animal()
animal.fly()  # 時速 20公里!
bird = Bird()
bird.fly(60)  # 時速 60公里!
plane = Plane()
plane.fly()  # 時速 1000 公里!
plane.fly_mile(5)  # 時速 5英哩!

animal = Animal()
animal.fly()  # 時速 20公里!
animal = Bird()
animal.fly(60)  # 時速 60公里!
animal = Plane()
animal.fly()  # 時速 1000 公里!
animal.fly_mile(5)  # 時速 5英哩!