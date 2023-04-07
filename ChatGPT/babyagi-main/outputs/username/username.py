import nltk
from nltk.corpus import words
from random import choice

nltk.download('words')
word_list = words.words()

word1 = choice(word_list)
word2 = choice(word_list)
username = f"{word1}_{word2}"
print(username)