class Dog:
 
    def make_sound(self):
        print("汪汪！")
 
class Cat:
 
    def make_sound(self):
        print("喵喵！")
 
class Car:
 
    def make_sound(self):
        print("叭叭！") 
 
# 多型展現：不管是狗、貓還是汽車，只要有 make_sound() 就能運作
def process_sound(obj):
    obj.make_sound()  # 這就是 Python 最典型的多型表現（鴨子型態）
 
process_sound(Dog())  # 汪汪！
process_sound(Cat())  # 喵喵！
process_sound(Car())  # 叭叭！