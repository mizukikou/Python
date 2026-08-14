class A:
    x = 1
 
class B(A):
    y = 2
 
class C(B):
    z = 3
 
obj = C()
print("x屬性的值為", obj.x)
print("y屬性的值為", obj.y)
print("z屬性的值為", obj.z)
print("C.__mro__:", C.__mro__)  # 顯示類別的繼承順序
print("B.__mro__:", B.__mro__)  # 顯示類別的繼承順序
print("A.__mro__:", A.__mro__)  # 顯示類別的繼承順序
print("object.__mro__:", object.__mro__)  # 顯示類別的繼承順序
print("C.__bases__:", C.__bases__)  # 顯示類別的父類別
print("B.__bases__:", B.__bases__)  # 顯示類別的父類別
print("A.__bases__:", A.__bases__)  # 顯示類別的父類別
print("object.__bases__:", object.__bases__)  # 顯示類別的父類別
print("C.__subclasses__():", C.__subclasses__())  # 顯示類別的子類別
print("B.__subclasses__():", B.__subclasses__())  # 顯示類別的子類別
print("A.__subclasses__():", A.__subclasses__())  # 顯示類別的子類別
