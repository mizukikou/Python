from functools import singledispatchmethod
 
class Calculator:
    # 1. 預設方法：當第一個參數是 int (或預設型態) 時執行
    @singledispatchmethod
    def add(self, x, y=None):
        # 情況 1：傳入兩個數字 -> 做數字相加
        if y is not None:
            return f"數字相加結果：{x + y}"
 
        # 情況 2：只傳入一個數字 -> 預設 +10
        return f"單一數字處理結果：{x + 10}"
 
    # 2. 註冊方法：當第一個參數 x 為 str (字串型態) 時自動分派到此方法
    @add.register
    def _(self, x: str, y: str):
        return f"字串串接結果：{x} - {y}"
 
# ==================== 測試執行 ====================
calc = Calculator()
 
# 1. 傳入 1 個參數 (int)
print(calc.add(5))  # 輸出：單一數字處理結果：15
 
# 2. 傳入 2 個數字型態參數 (int, int)
print(calc.add(10, 20))  # 輸出：數字相加結果：30
 
# 3. 傳入 2 個字串型態參數 (str, str)
print(calc.add("Hello", "World"))  # 輸出：字串串接結果：Hello - World 