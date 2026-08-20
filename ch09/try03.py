def dain(n1, n2):
    try:
        # 💡 使用 isinstance 檢查：如果 n1 是串列（List），才執行索引讀取
        if isinstance(n1, list):
            print(f"串列索引值為: {n1[n2]}")
            
        # 💡 如果 n1 不是串列（是數字），就直接執行除法運算
        else:
            print(f"{n1} / {n2} = {n1/n2}")
            
    except ZeroDivisionError:
        print("Error: division by zero")
    except IndexError:
        print("Error: index out of range")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Execution completed.")
        print("-" * 25) # 加上分隔線，讓輸出畫面更清晰

# ---- 主程式測試區 ----
arr = [0 for i in range(5)]

# 測試 1：觸發 IndexError（順利通過第一關的串列檢查，但索引 10 超出範圍）
dain(arr, 10)  

# 測試 2：觸發 ZeroDivisionError（走 else 路線，10/0 觸發除以零）
dain(10, 0)  

# 測試 3：正常執行（走 else 路線，10/2 完美印出 5.0）
dain(10, 2)  
