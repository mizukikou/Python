class Animal:
    def __init__(self, name):
        self.name = name

    def fly(self):
        print(f"{self.name}會飛喔")
        
class Bird(Animal):
    def __init__(self, name):
        # 1. 先叫爸爸準備好所有基礎屬性（包含未來可能新增的 hp, hungry 等）
        super().__init__(name) 
        
        # 下方子類別的 self.name 並不是創造了一個新變數，而是「直接覆蓋並取代」了父類別的 self.name
        #  self.name = name
        
        # 2. 拿回來之後，再把名字特製成粉紅色
        self.name = "粉紅色" + self.name
                
    def sing(self):
        print(f"{self.name},也愛唱歌喔")
        
print(Animal("小鳥")) #直接print物件，系統不知道要印出哪一個屬性，所以預設會印出這物件的「內部記憶體地址」。
print(Animal("小鳥").name)
print(Animal("小鳥").fly())
Animal("小鳥").fly()
print(Bird("小鳥").name)
print(Bird("小鳥").sing())
