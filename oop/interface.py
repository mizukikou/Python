from abc import ABC, abstractmethod

from abc import ABC, abstractmethod
class Animal(ABC):  # 介面（抽象類別）
    @abstractmethod
    def sound(self):
        pass

class Dog(Animal):
    def sound(self):
        return "汪汪"
class Cat(Animal):
    def sound(self):
        return "喵喵"
      
d = Dog()
print(d.sound())
c = Cat()
print(c.sound())