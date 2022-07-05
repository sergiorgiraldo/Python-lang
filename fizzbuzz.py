valor = 50
a = 1
while a < valor:
    if (a % 15 == 0):   
        print("fizzbuzz")
    elif (a % 3 == 0):   
        print("fizz")    
    elif (a % 5 == 0):   
        print("buzz")
    else:
        print(a)

    a = a + 1
