# -*- coding: utf-8 -*-

import re

ingredient = "Kumquat: 2 cups"

pattern_text = "(\w+):\s+(\d+)\s+(\w+)"
#pattern_text = r'(?P<ingredient>\w+):\s+(?P<amount>\d+)\s+(?P<unit>\w+)'
pattern = re.compile(pattern_text)

match = pattern.match(ingredient)

print(match)
print(match.groups())
print(match.group(1))

import random
some_list = [random.randint(1, 101) for i in range(100)] 
some_list

import os 
home = "C:/Users/sgiraldo/src/R-Lang" 
for dirname, dirnames, filenames in os.walk(home):
    for filename in filenames:
        print(os.path.join(dirname, filename))
