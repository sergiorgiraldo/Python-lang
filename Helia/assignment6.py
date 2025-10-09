if __name__ == "__main__":
    expenses = []
    expenses.append({"Category":"Eating Out", "Spent":50})
    expenses.append({"Category":"Groceries", "Spent":100})
    expenses.append({"Category":"Groceries", "Spent":30})
    expenses.append({"Category":"Travel", "Spent":18})
    expenses.append({"Category":"Travel", "Spent":2})
    expenses.append({"Category":"Auto", "Spent":78000.50})
    
    print(f"\n📅 Summary1-Letf")
    print("-" * 65)
    print(f"{'Category':<15}{'Spent':<20}")
    print("-" * 65)
    for e in expenses:
        print(f"{e['Category']:<15}{e['Spent']:<9.2f}") 

    print(f"\n📅 Summary2-Right")
    print("-" * 65)
    print(f"{'Category':>15}{'Spent':>20}")
    print("-" * 65)
    for e in expenses:
        print(f"{e['Category']:>15}{e['Spent']:>20.2f}")    #notice when you aligning right, you must reserve all width, 
                                                            #thats why i changed the float to be 20.2   

    print(f"\n📅 Summary3-Justified")
    print("-" * 65)
    print(f"{'Category':15}{'Spent':20}")
    print("-" * 65)
    for e in expenses:
        print(f"{e['Category']:15}{e['Spent']:9.2f}") 
