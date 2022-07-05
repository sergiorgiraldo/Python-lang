def test(nb):
    return (nb % 10 != 0)

#=================================================================#

lstNumbers = [1,2,3,4,5,6,7,8,9,10]

lstOdds = [i for i in lstNumbers if i % 2 == 0]

print(lstOdds)

lstEven = [i for i in lstNumbers if i not in lstOdds]

print(lstEven)

lstNumbers.extend([11,12,13,14,15,16,17,18,19,20])

print(lstNumbers)

lstNumbers.append(21)

print(lstNumbers)

lstNumbers = [i for i in lstNumbers if test(i)]

print(lstNumbers)

lstFives = [i for i in lstNumbers if i % 5 == 0 & (str(i)).endswith('5')]

print(lstFives)