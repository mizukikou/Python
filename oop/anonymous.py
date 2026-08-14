class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    def sing(self):
        print(f"{self.name},現在{self.age}歲,很會唱歌喔")
        
    def grow(self, age):
        self.age += age
        print(f"{self.name}長大了,現在{self.age}歲了")
        
bird = Animal("小鳥", 1)
#print(bird.name, bird.age)
bird.sing()
bird.grow(1)
print('=' * 20)
Animal("小雞", 2).sing()
Animal("小雞", 2).grow(1)
'''使用 print() 去包裹一個「沒有回傳值（return）」的方法。該方法執行完畢後就會預設回傳 None。'''
print(Animal("小雞", 2).sing())
print(Animal("小雞", 2).grow(1))

        
    