class Animal:
    def __init__(self, name):
        self.name = name
        print(f"[誕生] {self.name}被建立好了")
        
    def sing(self):
        print(f"{self.name},很會唱歌喔")
        
    def __del__(self):
        print(f"[銷毀] {self.name}離開了,記憶體空間已釋放")   
        
bird = Animal("小鳥")
print(bird.name)
bird.sing()
del bird
        
    