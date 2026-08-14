class Animal:
    def __init__(self, name, age):
        self.__name = name
        self.__age = age
        
    def __sing(self):
        print(f"{self.__name},現在{self.__age}歲,很會唱歌喔")
        
    def grow(self, age):
        self.__age += age
        print(f"{self.__name}長大了,現在{self.__age}歲了")
        
    def talk(self):
        self.__sing()
        
        
bird = Animal("小鳥", 1)
#print(bird.name, bird.age)
bird.talk()
bird.grow(1)
        
    