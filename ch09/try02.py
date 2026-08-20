def div(n1,n2):
    try:
        res = n1/n2
        print(f"{n1} / {n2} = {res}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Execution completed.")
    
div(8,2)  # 8 / 2 = 4.0
div(8,0)  # ZeroDivisionError: division by zero
