# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 14:38:57 2018

@author: sgiraldo
"""
print("******************")
print("******************")
print("******************")
print("lists are mutable")
print("******************")
l = ['a', 'b', 'mpilgrim', 'z', 'example'] 
print(l)
print(l[0])
print(l[1:])
print(l[:2])
print(l[-1])
print("******************")
b = [1,2]
print(b)
b = b + [3,4,5]
print(b)
b.extend([6,7,8])
print(b)
b.insert(2,99)
print(b)
b.append(666)
print(b)
print("******************")
c = [1,2,3,4,5,4,3,2,1]
print(c)
print(len(c))
print(c.count(2))
print(c.index(4))
print('1 in c ' + str(1 in c))
print('11 in c ' + str(11 in c))
print("******************")
print("******************")
print("******************")
print("tuples are immutable")
print("******************")
t1 = ('a', 'b', 'mpilgrim', 'z', 'example')
print(t1)
print(t1.index('z'))
print("******************")
print("******************")
print("******************")
print("sets are mutable")
print("******************")
s1 = {1,2,3}
print(s1)
s1.add(4)
print(s1)
print('2 in s1 ' + str(2 in s1))
print('22 in s1 ' + str(22 in s1))
print("******************")
print("******************")
print("******************")
print("dictionaries are mutable")
print("******************")
d1 = {'one':1,'two':2,'three':3}
print(d1)
d1['four']=5
print(d1)
d1['four']=4
print(d1)
d2 = {'tens':[10,11,12],'twenties':[25,26,27]}
print(d2)
print(d2['tens'])
print('tens in d2 '+ str('tens' in d2))
print('fifties in d2 '+ str('fifties' in d2))
