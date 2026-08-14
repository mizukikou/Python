class Calculator:
 
    def add(self, *args):
        # 情況 1：如果傳入 2 個參數
        if len(args) == 2:
            x, y = args[0], args[1]
            # 依據型態不同做不同處理
            if isinstance(x, str) and isinstance(y, str):
                return f"字串串接結果：{x} - {y}"
            return f"數字相加結果：{x + y}"
 
        # 情況 2：如果傳入 1 個參數，預設 +10
        elif len(args) == 1:
            x = args[0]
            # 🔒 安全防鎖：先確認這個進來的東西是不是真正的數字（int 或 float）
            if isinstance(x, (int, float)):
                return f"單一數字處理結果：{x + 10}"
            else:
                return f"錯誤：傳入一個參數時，必須是數字，不能是字串或字元 '{x}'！"

 
        # 防呆機制：處理傳入 0 個或 3 個以上參數的情況
        else:
            return "錯誤：不支援此參數數量！"
 
# ==================== 測試執行 ====================
calc = Calculator()
 
# 1. 傳入 1 個參數
print(calc.add(5))  # 輸出：單一數字處理結果：15
 
# 2. 傳入 2 個數字型態參數
print(calc.add(10, 20))  # 輸出：數字相加結果：30
  
# 3. 傳入 2 個字串型態參數
print(calc.add("Hello", "World"))  # 輸出：字串串接結果：Hello - World

# 4. 傳入 1 個參數
print(calc.add('A'))  # 輸出：錯誤：傳入一個參數時，必須是數字，不能是字串或字元 'A'！

