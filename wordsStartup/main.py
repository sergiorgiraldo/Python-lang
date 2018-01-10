import re

with open ("words_alpha.txt", "r") as myfile:
    allWords = myfile.readlines()

for word in allWords:
    if 'a' in word and 'd' in word and 'l' in word and 'u' in word and (len(word) == 4 or len(word) == 5 or len(word) == 6):
        print(word)