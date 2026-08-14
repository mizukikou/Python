class Father:  # 父類別 1
 
    def drive(self):
        print("會開車")
 
class Mother:  # 父類別 2
 
    def cook(self):
        print("會做飯")
 
# 多重繼承：Child 同時繼承了 Father 和 Mother
class Child(Father, Mother):
    pass
 
kid = Child()
kid.drive()  # 來自 Father
kid.cook()  # 來自 Mother