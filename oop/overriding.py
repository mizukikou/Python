class Calculator:
    # 透過預設參數 y=None, z=None 處理不同個數
    def add(self, x, y=None):
        # 情況 1：如果傳入兩個參數，做相加
        if y is not None:
            # 依據型態不同做不同處理
            # 變數 x 是否為字串型別
            if isinstance(x, str) and isinstance(y, str):
                return f"字串串接結果：{x} ~ {y}"
            return f"數字相加結果：{x + y}"
 
        # 情況 2：如果只傳入一個參數，預設 +10
        return f"單一數字處理結果：{x + 10}"
 
# ==================== 測試執行 ====================
calc = Calculator()
 
# 1. 傳入 1 個參數
print(calc.add(5))  # 輸出：單一數字處理結果：15
 
# 2. 傳入 2 個數字型態參數
print(calc.add(10, 20))  # 輸出：數字相加結果：30
 
# 3. 傳入 2 個字串型態參數
print(calc.add("Hello", "World"))  # 輸出：字串串接結果：Hello - World