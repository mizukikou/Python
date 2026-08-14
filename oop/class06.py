class Animal(): #定義父類別
    def __init__(self,name):
        self.name = name # 定義共用屬性
    def fly(self): #定義共用方法
        print(self.name+"很會飛!")
 
class Bird(Animal): #定義子類別
    def __init__(self,name,age):
        super().__init__(name) # 執行父類別的__init__()方法
        self.age = age #定義子類別共用屬性
    def fly(self): #定義子類別共用方法
        print(str(self.age)+"歲", end="")
        super().fly() # 執行父類別的 fly方法
 
if __name__ == "__main__":
    pigeon = Animal("小白鴿") # 以Animal類別建立一個名叫小白鴿的pigeon物件
    pigeon.fly() # 小白鴿很會飛!
    parrot = Bird("小鸚鵡",2) # 以Bird類別建立一個名叫小鸚鵡、2歲大的parrot物件
    parrot.fly() # 2歲小鸚鵡很會飛!